# Kimi Code CLI adapter

Kimi Code CLI is a first-class `vibe_start` target.

- Canonical project policy: `AGENTS.md`
- Canonical portable skills: `.agents/skills/`
- Kimi discovers project `.agents/skills/` natively, so no provider copy is required.
- Kimi may also discover `.kimi/skills/`, `.claude/skills/`, and `.codex/skills/`; avoid duplicate same-name skills when `vibe_start` already exposes the canonical generic root.
- Provider plugins/tools remain task-scoped and must not override the `AGENTS.md` contract.

The Kimi CLI project itself uses `AGENTS.md` for generated project guidance and documents `.agents/skills/` as a project-level skill root.
