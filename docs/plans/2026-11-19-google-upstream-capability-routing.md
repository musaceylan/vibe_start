# Plan: bounded routing for eight pinned Google and DeepMind projects

Date: 2026-11-19. Repositories: `vibe_start` (primary) and `vibe_backup`
(portable backup). Hermes stays the only orchestrator. Out of scope: commits,
pushes, remote changes, network access, package installs, clones, and any write
under `~/.vibe`.

## PRD

### Problem

Eight upstream projects were reviewed. Each needs an exact pin and a routing
decision. None of them may become a second control plane, a bulk-loaded
catalog, or a general install. The decisions must hold in both repositories,
each in its own schema.

### Requirements

| ID | Project @ pin | Decision |
| --- | --- | --- |
| R1 | `GoogleChrome/modern-web-guidance` @ `64a6d708f5a43f2cd3fde5d4d7db3905ba1bdf65` | Adopt now, read-only and on demand. Install only for the `frontend` and `full` profiles. Route browser compatibility, modern HTML/CSS, accessibility, Core Web Vitals, PWA, Web Components and WebMCP tasks. Dormant otherwise. |
| R2 | `google/skills` @ `06fff9e3edb7fc3c115a1769406047fcaf0a6289` | Add the pin; keep individual skills on demand; never bulk-activate. |
| R3 | `google/elephant-goldfish-model` @ `70406c4d22cc7ea8299637c2c5b44625c48b3f08` | Reference only; never install or activate the plugin. Hermes owns a local fresh-context design-review procedure, routed only for the explicit phrases `fresh-context review`, `fresh context review`, and `fresh-context design review`. Generic design/spec/architecture reviews remain dormant. |
| R4 | `google-labs-code/stitch-skills` @ `4cf4db8e4143b09e40f9bc887429d81f41ab3947` | Candidate; no global install. Isolated project-local pilot gated by Stitch MCP credentials, user approval before upload, a separate branch, one non-production screen, runtime screenshots at target viewports, and accessibility plus responsive validation. Prefer `generate-design`, `manage-design-system`, `react-components`, `validation`. |
| R5 | `a2ui-project/a2ui` @ `b4f91c26fcf62abc0720c21a65840220941d0a3f` | Project-specific reference; primary for A2UI/generative UI, AG-UI secondary. Bounded read-only React spike: result card, comparison chart, confirmation form; no external side effects; server auth/authz/validation/idempotency/audit; measure latency, tokens, schema failures and accessibility; pin versions. |
| R6 | `google-deepmind/mujoco` @ `be581a690cdd29846bb37cda425aa5d87511e26e` | Deferred reference. Route only robotics/physics/RL/simulation. MuJoCo 4.0.1+ and an isolated uv/Jetson benchmark before any project install. |
| R7 | `google-deepmind/detectorscope` @ `52ecc87775154b35d4550911de22faad4fc68f40` | Manual-only research reference. Never auto-route and never adjudicate people or content. |
| R8 | `google-deepmind/code-verification` @ `b0f729accbc21a0413e7ca4e1da43fa45b5f2e1b` | Formal-methods reference. Route Lean/AArch64/libsignal/formal crypto verification research only. Not a general code-security verifier. |

Cross-cutting: exact 40-character pins; no install except R1 in vibe_start;
English only; small surgical changes; existing fixtures and validations keep
passing.

### Non-goals

No external fetches to confirm upstream file layout or default branches; no
new orchestrator, hook, MCP server, or provider adapter; no license or score
claims that were not verified; no change to `~/.vibe` or `~/.hermes`.

### Acceptance criteria

- AC1: both repositories parse; only intended unstaged changes remain.
- AC2: all eight exact pins are present, and backup pins equal vibe_start pins.
- AC3: R1 routes on matching frontend tasks and never on unrelated backend
  tasks; only `--profile frontend|full` dry runs list it.
- AC4: `google/skills` stays non-installed and selective.
- AC5: Elephant-Goldfish appears only as a reference pin plus the local
  procedure, never as a routed specialist, install, or active ID.
- AC6: the Stitch and A2UI gates are explicit in procedures and metadata.
- AC7: MuJoCo and Code Verification are non-installed and route only on their
  narrow tasks; DetectorScope is a non-installed manual-only reference.
- AC8: `./vibe validate` and `./vibe benchmark` pass; the backup's
  `validate-capabilities.sh`, `doctor.sh`, `bash -n`, `install.sh --dry-run`
  and `git diff --check` pass apart from documented pre-existing warnings.

## Architecture

### vibe_start (scored router schema)

| Project | `repositories.lock.json` | Routing key (`routing.json` specialists) | `activation.json` mode |
| --- | --- | --- | --- |
| R1 | `active-specialist`, install, `["frontend","full"]` | `GoogleChrome/modern-web-guidance` | `read-only-on-demand` |
| R2 | `active-reference`, no install (pin added) | none (selected via `provider-skills`) | `skills-only-on-demand` |
| R3 | `reference`, no install | `hermes:fresh-context-design-review` (local key, not a repo) | `hermes-local-procedure` + procedure; EGM repo `reference-only`; `elephant-goldfish-full-plugin` joins `global-control-plane` |
| R4 | `candidate`, no install | `google-labs-code/stitch-skills` | `candidate-project-pilot` + procedure |
| R5 | `active-reference`, no install | `a2ui-project/a2ui`; `a2ui` added to `agent-ui` capability | `project-specific-reference` + procedure |
| R6 | `reference`, no install | `google-deepmind/mujoco` | `deferred-reference` |
| R7 | `reference`, no install | `google-deepmind/detectorscope` with empty routing patterns | `research-only`, manual selection only |
| R8 | `reference`, no install | `google-deepmind/code-verification` | `formal-methods-reference` |

Two backward-compatible router extensions in `scripts/route.py`:

1. `excludePatterns` (optional on any rule): a match zeroes that rule's score.
   It keeps the explicitly invoked design review away from UI design work,
   small fixes and test spec files. DetectorScope has no automatic patterns.
2. `procedure` passthrough: a specialist whose activation entry names a
   procedure gets an absolute `procedure` path in the route output.

Capability text (`capabilities.json`) records the ownership change:
A2UI is primary for `agent-ui` with AG-UI secondary, Modern Web Guidance is a
frontend secondary, and the procedures and references are listed with their
boundaries. `skills.json` lists Modern Web Guidance only as a task-scoped
frontend source, never as a portable or always-active skill.

### vibe_backup (Hermes catalog schema)

| Project | Provenance | Restore | Routing |
| --- | --- | --- | --- |
| R1, R2, R5, R6, R8 | `skills.lock.json` entry, `kind: reference` | `active-skills.json` `install:false` + `referenceRepositories` purpose | capability with `sourceRepo` and narrow triggers |
| R7 | `skills.lock.json` entry, `kind: reference` | `active-skills.json` `install:false` | manual-only capability with empty routing patterns |
| R3 | `skill-candidates.json` `reference-only` (Ponytail precedent) | never | capability `fresh-context-design-review` (local) + bundle `design-spec-review` |
| R4 | `skill-candidates.json` `candidate` | never | none; the candidate decision points to the pilot procedure |

New bundles: `design-spec-review`, `modern-web-platform` (the only bundle
holding Modern Web Guidance, which keeps it out of the general frontend and
performance bundles) and `generative-ui-spike`. The backup has no install
profiles, so R1 is not restored there; vibe_start installs it for
`frontend`/`full`. Lock entries use `branch: main` per convention; default
branches were not verified offline.

### Local procedures (identical copies in both repositories)

- `docs/procedures/fresh-context-design-review.md`
- `docs/procedures/stitch-project-pilot.md`
- `docs/procedures/a2ui-react-spike.md`

### Verification design

- `tests/test_upstream_capability_routing.py` (stdlib `unittest`, imports
  `scripts/route.py` in-process): exact pins, install boundaries via
  `install.sh --dry-run`, positive and negative routing for every project,
  procedure gate phrases, and regex compilation of every pattern.
- `tests/router-fixtures.json`: one positive case per routed project for
  `vibe validate` and `vibe benchmark`.
- `scripts/validate.sh` runs the unittest suite.
- Backup: a delimited boundary block in `scripts/validate-capabilities.sh`.

### Risks

| Risk | Mitigation |
| --- | --- |
| Broad words such as "simulation", "robots", "stitch", "lean" or "spec" misroute | Multi-word patterns, `excludePatterns`, and negative tests for each false-positive class |
| Specialist names read as fetchable repositories | Local key `hermes:` plus `reference-only` and `candidate` modes |
| Pins drift between repositories | Backup `doctor.sh` pin-agreement check and a cross-repo comparison in the report |
| Agent-written procedures treated as trusted | Left uncommitted for human review |

## Task list

1. Plan: this file. Done when it holds PRD, architecture and tasks.
2. RED (vibe_start): add `tests/test_upstream_capability_routing.py` and seven
   fixtures in `tests/router-fixtures.json`; run them and record the failures.
3. GREEN (vibe_start): edit `scripts/route.py`, `scripts/validate.sh`,
   `manifests/repositories.lock.json`, `manifests/routing.json`,
   `manifests/activation.json`, `manifests/capabilities.json`,
   `manifests/skills.json`; add the three procedures; rerun until green.
4. RED (vibe_backup): add the boundary block to
   `scripts/validate-capabilities.sh`; run it and record the failures.
5. GREEN (vibe_backup): edit `manifests/skills.lock.json`,
   `manifests/active-skills.json`, `manifests/skill-candidates.json`,
   `manifests/capabilities.json`, `manifests/bundles.json`; add the three
   procedures; rerun until green.
6. Docs: `README.md` (vibe_start); `README.md`, `REPO_SELECTION_V2.md`,
   `config/hermes/engineering/SKILL.md` (vibe_backup).
7. Verify: vibe_start `./vibe validate`, `./vibe benchmark`; vibe_backup
   `scripts/validate-capabilities.sh`, `scripts/doctor.sh`,
   `bash -n install.sh scripts/*.sh systemd/*.sh`, `./install.sh --dry-run`,
   `git diff --check`; cross-repo pin comparison; review both diffs.
