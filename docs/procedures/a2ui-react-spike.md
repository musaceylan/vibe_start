# A2UI React spike

A bounded, read-only spike before a project adopts A2UI. Source:
`a2ui-project/a2ui` at `b4f91c26fcf62abc0720c21a65840220941d0a3f`. A2UI is the
primary reference for A2UI and generative UI work. AG-UI stays secondary: use
it as the agent-to-frontend transport only where a project already relies on it.

## Scope

Render three components in the existing React app from agent-generated A2UI
messages:

1. **Result card:** read-only summary of one result.
2. **Comparison chart:** read-only comparison of two to five items.
3. **Confirmation form:** collects a confirmation and returns a dry-run
   response; it performs no action.

No external side effects: no writes, payments, emails, tickets, or third-party
API calls. Use fixture or sandbox data only.

## Server requirements

Any endpoint that receives a user action enforces, even during the spike:

- authentication and per-action authorization on the server;
- schema validation of every A2UI message and form payload, rejecting unknown
  components and properties;
- idempotency keys for confirmation submissions;
- an audit record (who, what, when, decision) without secrets or raw prompts.

The client renders only allowlisted components and treats agent output as
untrusted data.

## Measurements

Record for each component: end-to-end latency (p50 and p95), model tokens and
cost, schema validation failures and repairs, and accessibility results
(automated checks plus keyboard-only operation).

## Pinning

Pin the A2UI commit above, the renderer and package versions, and the model
version in the spike notes. Change them only together with a new measurement
run.

## Exit

A short report with the measurements and a recommendation. Adoption beyond the
spike needs human approval.
