# ADR-007 — Replay sandbox isolation (direction)
**Status:** proposed (benchmark required) · **Date:** 2026-10-04
## Context
Research 06 §8(iv): coding-agent state is overwhelmingly filesystem state; prefix re-execution in a pinned image reaches 99.99% return-code agreement; memory snapshots cost time proportional to RAM; E2B has native multi-fork; Daytona fork is filesystem-only and its OSS repo is unmaintained since June 2026.
## Decision (direction)
Tiered: containers with content-addressed filesystem snapshots as the default (R3); gVisor checkpoint/restore when process state matters, on the customer's runner; Firecracker memory-snapshot fork as the managed or high-isolation R4 tier. Network deny-by-default; no credentials mounted. Benchmark plan: `docs/phase0/benchmarks/sandbox.md`.
