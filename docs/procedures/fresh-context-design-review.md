# Fresh-context design review

Hermes-owned local procedure. Hermes is the sole orchestrator and reconciler.

Provenance: the fresh-context review pattern of `google/elephant-goldfish-model`
at `70406c4d22cc7ea8299637c2c5b44625c48b3f08`. That repository is a reference
only: never install, enable, or run its plugin, and never let it orchestrate
reviews beside Hermes.

## Use only for

- An explicit design, specification, RFC, or PRD review.
- An architecture or implementation plan review before code is written.

## Never use for

Small fixes, typos, hotfixes, one-line changes, ordinary bug fixes, review of
an existing code diff, or visual/UI design review. Those go to the normal
workflow, code-review, or frontend QA owners.

## Roles

| Role | Who | Context it receives |
| --- | --- | --- |
| Writer | one writer, an implementation-capable agent | full task context; the only author of the design |
| Assumptions reviewer | fresh, stateless session | the design artifact and this procedure only |
| Testability reviewer | fresh, stateless session | the design artifact and this procedure only |
| Reconciler | Hermes | the request, the design, and both reviews |
| Approver | human | the reconciled design and open risks |

Reviewers never see the writer's transcript, notes, or each other's findings,
and they never edit the design or the repository.

## Steps

1. **Write.** The writer produces one design artifact: goal, constraints,
   assumptions, interfaces, risks, and acceptance criteria.
2. **Review assumptions.** A fresh session lists unstated or unsupported
   assumptions, missing constraints, and contradictions, each with a severity
   and a quote from the artifact.
3. **Review testability.** A separate fresh session checks that every
   requirement has an observable acceptance criterion and a verification
   method, and lists untestable or ambiguous items.
4. **Reconcile.** Hermes merges the findings, removes duplicates, records each
   finding as accepted or rejected with a reason, and asks the writer for one
   revision.
5. **Approve.** Human approval before implementation is mandatory. The human
   approves, requests changes, or rejects; no implementation starts earlier.

## Budget

One writer, one review pass with two lenses run one after the other (only one
reviewer lane active at a time), and one revision. Another pass needs a new
human decision.

## Output

The reconciled design, a findings table (finding, lens, severity, decision,
reason), remaining risks, and the human decision.
