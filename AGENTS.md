<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

## ChatIndex Project Notes

This fork uses repo-local Spec Kit artifacts and normal project documentation to
keep planning, task scope, validation, and review gates explicit.

- `.specify/` contains Spec Kit templates, scripts, and project constitution.
- `specs/<feature-id>/` contains feature specs, plans, tasks, and checklists.

Do not store secrets, API keys, private OpenClaw logs, raw private sessions, or
generated executor run payloads in this repository. Runtime logs belong in
private OpenClaw storage, not committed repo files.
