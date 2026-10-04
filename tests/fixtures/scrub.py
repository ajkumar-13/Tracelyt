"""Scrub identifying values from captured Claude Code telemetry before committing as fixtures.
Replaces emails, account/org/user ids, device hashes, absolute scratch paths, and CCR session ids with stable placeholders."""
import re, sys, json, pathlib
RULES = [
    (re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}'), 'user@example.com'),
    (re.compile(r'user_[A-Za-z0-9]{20,}'), 'user_REDACTED'),
    (re.compile(r'cse_[A-Za-z0-9]{20,}'), 'cse_REDACTED'),
    (re.compile(r'[0-9a-f]{64}'), 'SHA256_REDACTED'),
    (re.compile(r'421c788f-d5cb-4ab1-a52e-3050b5aa74c2'), '00000000-0000-0000-0000-00000000org1'),
    (re.compile(r'2edccd78-b8b6-4eed-aebb-f0540a268235'), '00000000-0000-0000-0000-0000000acct1'),
    (re.compile(r'/tmp/claude-0/[^"\' ,}\]]*?scratchpad/proof([A-Z])(/runs/[A-Z0-9-]+)?'), r'/work/proof\1\2'),
    (re.compile(r'/tmp/claude-0/[^"\' ,}\]]*?scratchpad-proof([A-Z])(-runs-[A-Z0-9-]+)?'), r'/root/.claude/projects/-work-proof\1\2'),
    (re.compile(r'/tmp/claude-0/[^"\' ,}\]]*'), '/work/tmp'),
    (re.compile(r'sk-ant-[A-Za-z0-9_-]+'), 'sk-ant-REDACTED'),
]
def scrub(s):
    for rx, rep in RULES: s = rx.sub(rep, s)
    return s
if __name__ == '__main__':
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(scrub(src.read_text(errors='replace')))
