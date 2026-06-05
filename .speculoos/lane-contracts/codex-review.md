# Codex Review Lane Contract

## Role

Codex is the baseline reviewer and implementation assistant under OpenClaw
supervision.

## Inputs

- `.speculoos/goal.md`
- `.speculoos/manifest.yaml`
- `.speculoos/tasks/pr-000-fork-dev-baseline.yaml`
- `specs/000-fork-dev-baseline/`

## Required Outputs

- Review notes or proposed patch.
- Changed-file summary.
- Test commands and results.
- Acceptance or rejection rationale.

## Limits

Codex does not publish without the publish gate in
`.speculoos/lane-contracts/authority-boundaries.md`.
