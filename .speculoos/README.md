# Speculoos Workflow State

This directory stores repo-local workflow state for the ChatIndex fork.

- `goal.md`: objective, scope, gates, and acceptance criteria.
- `manifest.yaml`: canonical v0 state for task surfaces, lanes, and gates.
- `tasks/`: task-level readiness and acceptance records.
- `surfaces/`: external IDs and URLs for GitHub and Vibe Kanban.
- `lane-contracts/`: executor and authority boundaries.

Do not commit private run logs, provider keys, raw private sessions, or executor
payloads. Runtime artifacts belong in private OpenClaw storage.
