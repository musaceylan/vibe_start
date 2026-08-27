# Canonical Agent Skills root

This directory is the portable skill surface for `vibe_start` projects.

Do **not** vendor every curated skill here. `scripts/sync-skills.py` materializes only the skills selected for the target profile from pinned repositories installed under `VIBE_HOME`.

Rules:

- `AGENTS.md` always outranks third-party skill instructions.
- Installed does not mean loaded.
- A skill should be one focused capability with a `SKILL.md` entrypoint.
- Codex and Kimi can discover `.agents/skills/` directly.
- Qwen receives a `.qwen/skills/` projection to this canonical root.
- Claude may receive a `.claude/skills/` projection when explicitly requested.
- Provider projections are symlinks where possible; do not fork/copy skill content unnecessarily.
- Conflicting or benchmark-only skills are never projected automatically.
