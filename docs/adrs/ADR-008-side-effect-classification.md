# ADR-008 — Side-effect classification of tools and MCP servers
**Status:** accepted (v0.1) · **Date:** 2026-10-04
## Decision
Classes: `read_only`, `reversible_write`, `irreversible_write`, `financial`, `security_sensitive`, `external_communication`, `unknown`. Sources, in precedence: MCP tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), customer declaration, builtin tables (Claude Code builtins; shell binaries), inference, default `unknown`. `unknown` is treated as irreversible by replay. The class, its source and confidence are recorded on every tool request.
