# Stitch project-local pilot

Status: candidate. Source: `google-labs-code/stitch-skills` at
`4cf4db8e4143b09e40f9bc887429d81f41ab3947`. Never install it globally: no
user-level settings, shared skill roots, or default profiles.

## Gates (all required before the first Stitch call)

1. **Credentials:** Stitch MCP credentials come from the environment or an
   ignored local file in the pilot project. Never commit, log, or paste them.
2. **Approval before upload:** the user approves each external upload
   (prompts, screenshots, design tokens) before it leaves the machine.
3. **Isolation:** a separate branch in one pilot project. Skills are linked
   project-locally and removed if the pilot is not promoted.
4. **Scope:** one non-production screen. No customer data, secrets, unreleased
   product details, or production design-system source.

## Allowed skills

Prefer only `generate-design`, `manage-design-system`, `react-components`, and
`validation`. Confirm their paths at the pinned commit before linking them, and
load no other Stitch skill during the pilot.

## Steps

1. Record the pinned commit, the screen, the target viewports, and the user
   approval.
2. Generate the design, then manage only the design-system tokens that screen
   needs.
3. Build the React components on the pilot branch.
4. Run the `validation` skill and the project's own checks.

## Required evidence

- Runtime screenshots of the running app at every target viewport (for
  example 375, 768, and 1440 px wide); design-tool exports do not count.
- Accessibility validation: automated checks plus keyboard and screen-reader
  spot checks, with no critical findings.
- Responsive validation: no horizontal overflow, clipped content, or overlap
  at any target viewport.

## Exit

Promotion needs every curation gate, a recorded review of the evidence, and
human approval. Otherwise delete the pilot branch and the project-local links.
