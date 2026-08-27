# Qwen Code adapter

Qwen Code reads the repository `AGENTS.md` directly, so `vibe_start` does **not** duplicate canonical policy into `QWEN.md`.

- Canonical project policy: `AGENTS.md`
- Canonical portable skills: `.agents/skills/`
- Qwen project skill view: `.qwen/skills/`
- `scripts/sync-skills.py` may create symlinks from `.qwen/skills/` to `.agents/skills/`.
- Existing `QWEN.md` remains project/provider-specific and is never overwritten by `vibe_start`.

Official Qwen Code documentation currently documents project skills under `.qwen/skills/` and states that an existing `AGENTS.md` is read without needing duplicated instructions.
