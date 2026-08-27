# OpenCode compatibility

`vibe_start` treats OpenCode as a compatibility target, but does not generate provider-specific settings until current official syntax is verified.

Fallback contract:

1. Read `START_HERE.md`.
2. Read and obey `AGENTS.md` as canonical policy.
3. Route the task with `vibe route` when available.
4. Use selected `.agents/skills/` entries manually if the host does not discover the generic Agent Skills root natively.

Do not copy large policy blocks into provider files merely for compatibility.
