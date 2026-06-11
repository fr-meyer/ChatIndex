<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

## Speculoos Workflow

This fork uses repo-local Spec Kit artifacts plus `.speculoos/` workflow state
to keep planning, task surfaces, executor lanes, and review gates explicit.

- `.specify/` contains Spec Kit templates, scripts, and project constitution.
- `specs/<feature-id>/` contains feature specs, plans, tasks, and checklists.
- `.speculoos/manifest.yaml` is the v0 workflow manifest.
- `.speculoos/tasks/` contains task readiness and acceptance state.
- `.speculoos/surfaces/` records external issue/project/workspace mappings.
- `.speculoos/lane-contracts/` defines executor and authority boundaries.

Do not store secrets, API keys, private OpenClaw logs, raw private sessions, or
generated executor run payloads in this repository. Runtime logs belong in
private OpenClaw storage, not committed repo files.
