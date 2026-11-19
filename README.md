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

`vibe route` returns a base profile plus **multiple capabilities**, task specialists, independent verification steps, risk level and a context budget. A task can therefore resolve to `frontend + marketing + testing + debugging` instead of being forced into one coarse profile. A specialist backed by a local procedure also returns its absolute `procedure` path; a rule's optional `excludePatterns` veto it for look-alike tasks.

## Curated overlap policy

Large systems such as ECC, Context Mode, Impeccable and context-engineering skill collections are curated without automatically becoming another operating system:

- **ECC:** selective procedures/reference only under Hermes; never full-harness co-activation.
- **Context Mode / Headroom:** benchmark candidates for context/tool-output optimization.
- **Impeccable:** frontend audit/verification specialist, not another always-on design baseline.
- **Agent Skills for Context Engineering:** individual task-scoped skills only.

Google and DeepMind projects reviewed on 2026-11-19 are exact-pinned in `manifests/repositories.lock.json` with narrow routes:

- **Modern Web Guidance:** read-only; installed only by the `frontend` and `full` profiles; routed only for browser compatibility, modern HTML/CSS, accessibility, Core Web Vitals, PWA, Web Components and WebMCP.
- **Google Skills:** individual Google-product skills on demand; the catalog is never bulk-activated.
- **Elephant-Goldfish:** reference only; its plugin is never installed. Hermes owns the local [fresh-context design review](docs/procedures/fresh-context-design-review.md), invoked only by the explicit `fresh-context review` phrase.
- **Stitch Skills:** candidate; only the gated [project-local pilot](docs/procedures/stitch-project-pilot.md), never a global install.
- **A2UI:** primary project-specific reference for A2UI/generative UI, AG-UI secondary; start with the bounded [read-only React spike](docs/procedures/a2ui-react-spike.md).
- **MuJoCo, DetectorScope, Code Verification:** never installed. MuJoCo and Code Verification route only for their narrow simulation and formal-methods tasks. DetectorScope is manual-only research reference material and never auto-routes or adjudicates people or content.

See `manifests/activation.json`, `manifests/providers.json`, `manifests/routing.json`, and `manifests/curation-policy.json` for the machine-readable rules.
