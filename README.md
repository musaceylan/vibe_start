# vibe_start

Universal, low-context engineering layer for **Claude Code, Codex, Kimi Code CLI, Qwen Code, Gemini CLI, Cursor, Copilot, Hermes**, and future `AGENTS.md` / Agent-Skills-compatible coding agents.

`vibe_start` is a **capability router and compatibility layer**, not an awesome-list and not a second orchestrator. It curates broad knowledge, but runtime loads only the smallest task-relevant capabilities and specialists.

## Architecture

```text
                         vibe_start
                             |
               +-------------+-------------+
               |                           |
           AGENTS.md                 .agents/skills/
       canonical policy            canonical skills
               |                           |
        scored capability             native / projected
            routing                    provider views
               |                           |
      Hermes when present       Codex  Kimi  Qwen  Claude ...
               |
        task specialists
               |
     independent verification
```

Core rules:

- **One control plane:** Hermes when present; otherwise the host agent routes from the manifests.
- **Installed != loaded.** Installation is profile-aware; activation is task-aware.
- **Overlap != exclusion.** Assign one owner, specialists, benchmark candidates, and explicit non-coactivation rules.
- **Canonical portable skills:** `.agents/skills/`. Codex and Kimi consume it natively; Qwen receives a safe `.qwen/skills/` projection.
- **Provider adapters stay thin.** They point to `AGENTS.md` rather than duplicating policy.
- **Progressive disclosure:** deterministic inspection first, then symbols/AST, then specialist/deep context only when evidence justifies it.
- **Creation and verification are separate.** Example: frontend create -> motion -> deterministic audit -> Playwright/accessibility verification.
- **Third-party skills/hooks/MCP/repos are untrusted supply-chain input.** Promotion is gated and never automatic.

## Start

```bash
# Install only the safe baseline
./vibe install --profile safe

# Or install the pinned frontend sources
./vibe install --profile frontend

# Fingerprint a project
./vibe init /path/to/project

# Preview/apply thin provider adapters
./vibe settings /path/to/project
./vibe settings /path/to/project --apply

# Preview/apply portable skill projections
./vibe skills /path/to/project
./vibe skills /path/to/project --providers qwen,claude --apply

# Route a compound task
./vibe route --project /path/to/project --task "audit and animate the landing page for SEO and accessibility"

# Integrity / regression checks
./vibe doctor
./vibe validate
./vibe benchmark

# Review candidate promotion queue; never auto-promotes
./vibe update
```

## What routing returns

`vibe route` returns a base profile plus **multiple capabilities**, task specialists, independent verification steps, risk level and a context budget. A task can therefore resolve to `frontend + marketing + testing + debugging` instead of being forced into one coarse profile.

## Curated overlap policy

Large systems such as ECC, Context Mode, Impeccable and context-engineering skill collections are curated without automatically becoming another operating system:

- **ECC:** selective procedures/reference only under Hermes; never full-harness co-activation.
- **Context Mode / Headroom:** benchmark candidates for context/tool-output optimization.
- **Impeccable:** frontend audit/verification specialist, not another always-on design baseline.
- **Agent Skills for Context Engineering:** individual task-scoped skills only.

See `manifests/activation.json`, `manifests/providers.json`, `manifests/routing.json`, and `manifests/curation-policy.json` for the machine-readable rules.
