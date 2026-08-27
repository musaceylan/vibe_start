# Agent settings governance

`vibe_start` manages agent settings as a thin compatibility layer around the canonical `AGENTS.md` contract.

## Precedence

1. Existing repository rules and safety constraints remain in force.
2. `AGENTS.md` is the shared canonical contract.
3. Provider-native files are adapters, not independent policy sources.
4. Project-specific configuration must not be copied into global configuration.
5. A provider adapter must never weaken a stricter existing rule.

## Safe update rules

- Default to dry-run.
- Do not overwrite existing agent files silently.
- If an existing adapter already references `AGENTS.md`, preserve it.
- If an adapter exists without the bridge, explicit `--apply` may append only the canonical-policy bridge after creating a timestamped backup.
- Never enable unrestricted permissions, destructive git behavior, secret access, production deployment, or broad network access by default.
- Never install third-party hooks, skills, MCP servers, binaries, or repositories as part of settings generation.
- Unsupported or uncertain provider schemas must be documented/researched before adding a native settings writer.
- Keep generated adapters small; durable shared rules belong in `AGENTS.md`, specialized workflows in skills, and long details in references.

## Usage

Preview changes:

```bash
./vibe settings /path/to/project
```

Apply supported adapters:

```bash
./vibe settings /path/to/project --apply
```

Select adapters:

```bash
./vibe settings /path/to/project --agents claude,gemini,copilot,cursor --apply
```

## Supported adapters

The bootstrap currently writes only provider-native instruction bridges whose syntax is sufficiently stable and whose behavior does not require granting permissions:

- Claude Code: `CLAUDE.md`
- Gemini CLI: `GEMINI.md`
- GitHub Copilot: `.github/copilot-instructions.md`
- Cursor: `.cursor/rules/vibe-start.mdc`

Codex consumes the repository's native `AGENTS.md` hierarchy, so no duplicate instruction file is created. Hermes remains the orchestrator when present and must not be replaced by another orchestration layer.

Provider-specific settings such as permission models, hooks, MCP, sandbox/network policies, reasoning defaults, or global configuration should only be added after current official documentation is verified and the proposed change is representable without overriding user/project policy.
