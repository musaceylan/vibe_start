# Architecture

`vibe_start` separates **curation**, **installation**, **runtime routing**, **provider compatibility**, and **verification** so a large knowledge catalog does not become a large prompt or a stack of competing orchestrators.

## Layers

1. **Canonical policy — `AGENTS.md`**  
   Universal behavior, safety, context and governance. Provider files may bridge to it but must not duplicate or weaken it.

2. **Project fingerprint — `.vibe/project.json`**  
   Detected languages, frameworks, build/test systems and infrastructure. It informs routing but may be overridden deliberately.

3. **Capability routing — `routing.json` + `capabilities.json`**  
   Scored multi-capability selection. A task can resolve to several capabilities instead of one coarse profile.

4. **Ownership/conflicts — `activation.json`**  
   Overlapping projects remain curated, but one owner handles each job. Specialists and benchmark candidates have explicit activation modes; global control planes do not co-activate.

5. **Portable skill plane — `.agents/skills/`**  
   Selected skills are linked from pinned repositories into one canonical project root. Codex and Kimi can consume this root directly; Qwen and other providers may receive projections without copying policy/content.

6. **Tool/MCP plane — `tools.json` + `mcp/catalog.json`**  
   Tools carry role, context-cost and risk metadata. Runtime chooses the smallest safe tool rather than enabling every integration.

7. **Semantic hooks — `hooks/events.json`**  
   Provider-neutral lifecycle events. Native provider syntax is rendered only after current official behavior is verified.

8. **Memory — `memory.json` + schema**  
   Typed durable knowledge with evidence/lifecycle metadata. Retrieval is task-filtered; secrets and raw tool noise are forbidden.

9. **Evaluation — router fixtures + `vibe benchmark`**  
   Routing is regression-tested. Runtime/context replacements must prove task success and defect quality, not merely token savings.

10. **Curation gates — `curation-policy.json`**  
    Discover → inspect provenance/license/security → assign overlap ownership → benchmark when behavior changes → pin executable dependencies → human approval. No auto-promotion.

## Control plane

Hermes is the preferred global orchestrator when present. `repo-harness` is repository execution beneath it. Superpowers, ECC, BMAD, ruflo, Ralph and similar systems may contribute isolated procedures, but a second global orchestrator is not activated beside Hermes.

Without Hermes, the host agent follows the same manifests directly.

## Context discipline

Runtime uses progressive disclosure: universal policy → project fingerprint → task evidence → selected capability → specialist → deep research. Deterministic/symbolic inspection precedes broad semantic or LLM-heavy analysis.

## Verification independence

Creation and verification should use different evidence where possible. For frontend work, for example: create with the frontend baseline/Taste, animate with GSAP if required, inspect with deterministic design checks, then verify with project tests/accessibility/Playwright.
