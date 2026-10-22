"""A scripted `agents.Model` for exercising the OpenAI Agents SDK without an API key or network.

The model returns a predetermined sequence of `ModelResponse`s. It opens a `generation` span and fills it the way
the SDK's own Chat Completions model does (`input`, `output`, `model`, `model_config`, `usage`), so the
tracing processor sees the same span shape it sees in production. Every id is deterministic, so two runs of the
same script produce byte-identical payloads (span and trace ids are the SDK's own and still differ per run).

Importing this module requires `openai-agents`; the rest of `harness_engine` does not.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from agents import Model, ModelResponse, ModelSettings, Usage
from agents.tracing import generation_span
from openai.types.responses import (Response, ResponseCompletedEvent, ResponseFunctionToolCall, ResponseOutputMessage,
                                    ResponseOutputText, ResponseUsage)
from openai.types.responses.response_usage import InputTokensDetails, OutputTokensDetails

MODEL_NAME = "scripted-model-1"


def text(msg: str, item_id: str) -> ResponseOutputMessage:
    return ResponseOutputMessage(id=item_id, type="message", role="assistant", status="completed",
                                 content=[ResponseOutputText(text=msg, type="output_text", annotations=[], logprobs=[])])


def call(name: str, arguments: dict | str, call_id: str) -> ResponseFunctionToolCall:
    args = arguments if isinstance(arguments, str) else json.dumps(arguments, sort_keys=True)
    return ResponseFunctionToolCall(id=f"fc_{call_id}", call_id=call_id, name=name, arguments=args, type="function_call", status="completed")


def compaction(item_id: str, encrypted_content: str = "c2NyaXB0ZWQtY29tcGFjdGlvbg==") -> dict:
    """A Responses API `compaction` output item (what server-side context management returns)."""
    return {"type": "compaction", "id": item_id, "encrypted_content": encrypted_content}


@dataclass
class Step:
    """One scripted model turn. `output` items are returned as-is; `expect_agent` asserts which agent is calling."""
    output: list[Any]
    input_tokens: int = 100
    output_tokens: int = 20
    expect_agent: str | None = None


@dataclass
class ScriptedModel(Model):
    steps: list[Step]
    name: str = MODEL_NAME
    calls: list[dict] = field(default_factory=list)
    on_call: Callable[[int, str | None], None] | None = None

    def _next(self, system_instructions: str | None, input: Any, tools: Sequence[Any], handoffs: Sequence[Any]) -> tuple[int, Step]:
        i = len(self.calls)
        if i >= len(self.steps):
            raise RuntimeError(f"ScriptedModel exhausted after {i} calls")
        self.calls.append({"index": i, "num_input_items": len(input) if isinstance(input, list) else 1,
                           "tools": sorted(getattr(t, "name", str(t)) for t in tools),
                           "handoffs": sorted(getattr(h, "tool_name", str(h)) for h in handoffs)})
        if self.on_call: self.on_call(i, system_instructions)
        return i, self.steps[i]

    def _usage(self, step: Step) -> Usage:
        return Usage(requests=1, input_tokens=step.input_tokens, output_tokens=step.output_tokens,
                     total_tokens=step.input_tokens + step.output_tokens)

    def _response(self, i: int, step: Step) -> Response:
        return Response(id=f"resp_scripted_{i:03d}", created_at=0, model=self.name, object="response", output=step.output,
                        tool_choice="auto", tools=[], parallel_tool_calls=False,
                        usage=ResponseUsage(input_tokens=step.input_tokens, output_tokens=step.output_tokens,
                                            total_tokens=step.input_tokens + step.output_tokens,
                                            input_tokens_details=InputTokensDetails(cached_tokens=0, cache_write_tokens=0),
                                            output_tokens_details=OutputTokensDetails(reasoning_tokens=0)))

    def _fill_span(self, span: Any, input: Any, model_settings: ModelSettings, step: Step, resp: Response, tracing: Any) -> None:
        span.span_data.model = self.name
        span.span_data.model_config = model_settings.to_json_dict() | {"base_url": "scripted://local"}
        if tracing.include_data():
            span.span_data.input = input if isinstance(input, list) else [{"role": "user", "content": input}]
            span.span_data.output = [resp.model_dump(mode="json", exclude_none=True)]
        span.span_data.usage = {"requests": 1, "input_tokens": step.input_tokens, "output_tokens": step.output_tokens,
                                "total_tokens": step.input_tokens + step.output_tokens}

    async def get_response(self, system_instructions, input, model_settings, tools, output_schema, handoffs, tracing, *,
                           previous_response_id=None, conversation_id=None, prompt=None) -> ModelResponse:
        with generation_span(model=self.name, disabled=tracing.is_disabled()) as span:
            i, step = self._next(system_instructions, input, tools, handoffs)
            resp = self._response(i, step)
            self._fill_span(span, input, model_settings, step, resp, tracing)
            return ModelResponse(output=list(step.output), usage=self._usage(step), response_id=resp.id, request_id=f"req_scripted_{i:03d}")

    async def stream_response(self, system_instructions, input, model_settings, tools, output_schema, handoffs, tracing, *,
                              previous_response_id=None, conversation_id=None, prompt=None) -> AsyncIterator[Any]:
        with generation_span(model=self.name, disabled=tracing.is_disabled()) as span:
            i, step = self._next(system_instructions, input, tools, handoffs)
            resp = self._response(i, step)
            self._fill_span(span, input, model_settings, step, resp, tracing)
            yield ResponseCompletedEvent(type="response.completed", response=resp, sequence_number=0)
