# Agent settings governance

`vibe_start` manages agent settings as a thin compatibility layer around the canonical `AGENTS.md` contract and canonical `.agents/skills/` project skill root.

## Precedence

1. Existing repository rules and safety constraints remain in force.
2. `AGENTS.md` is the shared canonical contract.
3. Provider-native files are adapters, not independent policy sources.
4. Project-specific configuration must not be copied into global configuration.
5. A provider adapter must never weaken a stricter existing rule.
6. Third-party skills/tools cannot override canonical policy.

## Safe update rules

- Default to dry-run.
- Do not overwrite existing agent files silently.
- If an existing adapter already references `AGENTS.md`, preserve it.
- If an adapter exists without the bridge, explicit `--apply` may append only the canonical-policy bridge after creating a timestamped backup.
- Native `AGENTS.md` consumers should not get redundant policy files just for symmetry.
- Never overwrite an existing `QWEN.md`; Qwen already reads `AGENTS.md` and `QWEN.md` remains provider/project-specific.
- Never enable unrestricted permissions, destructive git behavior, secret access, production deployment, or broad network access by default.
- Never install third-party hooks, MCP servers or binaries as a side effect of settings generation.
- Unsupported or uncertain provider schemas must be verified before adding a native settings writer.
- Keep generated adapters small; durable shared rules belong in `AGENTS.md`, specialized workflows in skills, and long details in references.

## Canonical skills

`.agents/skills/` is the project-level portable skill surface. Use `vibe skills` to materialize only selected skills from pinned repositories.

- Codex: consumes repository `.agents/skills/` natively.
- Kimi Code CLI: consumes repository `.agents/skills/` natively.
- Qwen Code: official project skill root is `.qwen/skills/`; `vibe skills` creates a projection to the canonical root.
- Claude Code: a `.claude/skills/` projection may be created when explicitly requested/detected.
- Other agents: use native skill roots only after current behavior is verified; otherwise read the selected canonical skill manually.

Provider projections are symlinks where possible and existing directories/files are preserved rather than replaced.

## Usage

Preview settings changes:

```bash
./vibe settings /path/to/project
```

Apply supported file adapters:

```bash
./vibe settings /path/to/project --apply
```

Select agents, including native/no-write consumers:

```bash
./vibe settings /path/to/project --agents claude,codex,kimi,qwen,gemini,cursor,copilot,hermes --apply
```

Preview portable skills:

```bash
./vibe skills /path/to/project
```

Apply Qwen/Claude projections when needed:

```bash
./vibe skills /path/to/project --providers qwen,claude --apply
```

## Supported behavior

- Claude Code: thin `CLAUDE.md` bridge.
- Gemini CLI: thin `GEMINI.md` bridge.
- GitHub Copilot: thin `.github/copilot-instructions.md` bridge.
- Cursor: thin `.cursor/rules/vibe-start.mdc` bridge.
- Codex: native `AGENTS.md` + native generic skills; no duplicate policy write.
- Kimi Code CLI: native `AGENTS.md` + native generic skills; no duplicate policy write.
- Qwen Code: native `AGENTS.md`; preserves `QWEN.md`; skill projection only when requested.
- Hermes: orchestrator bridge; does not create another project policy source.
- Generic compatible agent: read `START_HERE.md` then `AGENTS.md`; manually load routed skills when native discovery is unavailable.

Provider-specific permission models, native hooks, MCP configuration, sandbox/network policies, reasoning defaults or global configuration are added only after current official documentation is verified and the change is representable without overriding user/project policy.
