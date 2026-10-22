"""Replay server: speaks the Anthropic Messages API (streaming) and serves recorded responses by S1 match.

Point the harness at it with ANTHROPIC_BASE_URL=http://127.0.0.1:<port>. Every request is logged to
<out_dir>/replay_requests.jsonl; unknown endpoints get a JSON error and are logged as `unmatched_endpoint`.
"""
from __future__ import annotations
import gzip, json, os, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .cassette import Cassette
from .match import Matcher


def sse_events(msg: dict):
    """Turn a stored (non-streamed) message into the Messages API streaming event sequence."""
    usage = dict(msg.get("usage") or {})
    out_tokens = usage.pop("output_tokens", 0)
    head = {k: msg.get(k) for k in ("id", "type", "role", "model")}
    head.update({"content": [], "stop_reason": None, "stop_sequence": None, "usage": {**usage, "output_tokens": 1}})
    yield "message_start", {"type": "message_start", "message": head}
    for i, b in enumerate(msg.get("content", [])):
        t = b.get("type")
        if t == "thinking":
            yield "content_block_start", {"type": "content_block_start", "index": i, "content_block": {"type": "thinking", "thinking": ""}}
            yield "content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "thinking_delta", "thinking": b.get("thinking", "")}}
            if b.get("signature"):
                yield "content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "signature_delta", "signature": b["signature"]}}
        elif t == "redacted_thinking":
            yield "content_block_start", {"type": "content_block_start", "index": i, "content_block": b}
        elif t == "text":
            yield "content_block_start", {"type": "content_block_start", "index": i, "content_block": {"type": "text", "text": ""}}
            yield "content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "text_delta", "text": b.get("text", "")}}
        elif t == "tool_use":
            start = {"type": "tool_use", "id": b["id"], "name": b["name"], "input": {}}
            if "caller" in b: start["caller"] = b["caller"]
            yield "content_block_start", {"type": "content_block_start", "index": i, "content_block": start}
            yield "content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "input_json_delta", "partial_json": json.dumps(b.get("input", {}))}}
        else:
            yield "content_block_start", {"type": "content_block_start", "index": i, "content_block": b}
        yield "content_block_stop", {"type": "content_block_stop", "index": i}
    delta = {"stop_reason": msg.get("stop_reason"), "stop_sequence": msg.get("stop_sequence")}
    if msg.get("stop_details") is not None: delta["stop_details"] = msg["stop_details"]
    yield "message_delta", {"type": "message_delta", "delta": delta, "usage": {**usage, "output_tokens": out_tokens}}
    yield "message_stop", {"type": "message_stop"}


class ReplayServer:
    def __init__(self, cassette: Cassette, out_dir: str, policy: str = "report", host: str = "127.0.0.1", port: int = 0):
        self.cassette, self.out_dir, self.policy = cassette, out_dir, policy
        os.makedirs(out_dir, exist_ok=True)
        self.matcher = Matcher(cassette, policy)
        self.log_path = os.path.join(out_dir, "replay_requests.jsonl")
        self.unmatched_endpoints: list[dict] = []
        self._lock = threading.Lock()
        srv = self

        class H(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a): pass

            def _body(self):
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                if self.headers.get("Content-Encoding") == "gzip": raw = gzip.decompress(raw)
                return raw

            def _json(self, code: int, obj: dict):
                data = json.dumps(obj).encode()
                self.send_response(code); self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

            def do_GET(self):
                srv._log({"ts": time.time(), "method": "GET", "path": self.path, "kind": "unmatched_endpoint"})
                self._json(404, {"type": "error", "error": {"type": "not_found_error", "message": "replay server: no fixture for this endpoint"}})

            def do_POST(self):
                raw = self._body()
                path = self.path.split("?")[0]
                if not path.endswith("/v1/messages"):
                    srv._log({"ts": time.time(), "method": "POST", "path": self.path, "kind": "unmatched_endpoint", "bytes": len(raw)})
                    srv.unmatched_endpoints.append({"path": self.path})
                    self._json(404, {"type": "error", "error": {"type": "not_found_error", "message": "replay server: no fixture for this endpoint"}})
                    return
                try:
                    req = json.loads(raw)
                except Exception:
                    self._json(400, {"type": "error", "error": {"type": "invalid_request_error", "message": "bad json"}}); return
                with srv._lock:
                    r = srv.matcher.match(req)
                srv._log({"ts": time.time(), "method": "POST", "path": self.path, "kind": "model_call", "seq": r.seq, "level": r.level,
                          "candidate_index": r.envelope.index if r.envelope else None,
                          "stream": bool(req.get("stream")), "model": req.get("model"),
                          "config_drift": None if not r.config_drift else r.config_drift[:6],
                          "divergence": None if not r.divergence else {"reason": r.divergence.reason, "field_diff": r.divergence.field_diff[:10]}})
                if r.envelope is None:
                    # No fixture. Harness side calls (post-turn summaries, title generation) land here after the
                    # recorded turn is complete; the harness tolerates the error and the run still ends normally.
                    self._json(409, {"type": "error", "error": {"type": "replay_divergence", "message": (r.divergence.reason if r.divergence else "no candidate")}})
                    return
                msg = r.envelope.response
                if req.get("stream"):
                    self.send_response(200); self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache"); self.send_header("request-id", r.envelope.request_id or "replay")
                    self.send_header("Transfer-Encoding", "chunked"); self.end_headers()
                    for name, ev in sse_events(msg):
                        chunk = f"event: {name}\ndata: {json.dumps(ev)}\n\n".encode()
                        self.wfile.write(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n"); self.wfile.flush()
                    self.wfile.write(b"0\r\n\r\n"); self.wfile.flush()
                else:
                    self._json(200, msg)

        self.httpd = ThreadingHTTPServer((host, port), H)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def _log(self, rec: dict):
        with self._lock:
            with open(self.log_path, "a") as f: f.write(json.dumps(rec) + "\n")

    def start(self): self.thread.start(); return self

    def stop(self): self.httpd.shutdown(); self.httpd.server_close()

    @property
    def base_url(self) -> str: return f"http://127.0.0.1:{self.port}"
