# Hooks

`vibe_start` defines **semantic lifecycle events** in `hooks/events.json`; provider-specific hook syntax is an adapter detail.

- **ALWAYS**: cheap deterministic routing and destructive/credential-risk guards.
- **CONDITIONAL**: compact evidence capture, pre-commit verification, context preservation, browser QA.
- **MANUAL**: deep architecture audits, heavy semantic indexing, experimental context proxies.

Rules:

1. Hooks must have measurable benefit, bounded runtime and explicit failure behavior.
2. A third-party plugin may not silently register a second global control plane.
3. Provider hook configs are rendered only after current official syntax is verified.
4. High-risk guards fail closed; optimization/telemetry hooks fail open.
5. Raw tool output is never promoted into durable memory by default.
6. Context Mode, Headroom or similar interception layers remain benchmark/opt-in, not always-on hooks.
