# Goal: ChatIndex Speculoos Closure

## Objective

Close the initial ChatIndex roadmap dogfood loop with one composed no-key smoke
test and accurate Speculoos surface metadata.

## Scope

- Keep PR001-PR004 recorded as merged/done.
- Add no-key smoke coverage proving save/load, incremental append, vector
  search, and message-range retrieval compose.
- Keep GitHub Project, Vibe Kanban, and repo-local metadata synchronized.
- Preserve the no-secret validation path for future roadmap or hardening PRs.

## Non-goals

- Add new roadmap features beyond the closure smoke test.
- Promote fork `dev` to `main`.
- Commit private OpenClaw logs or real provider responses.

## Stop Conditions

- Fork visibility or GitHub/Project auth is missing when a publish action is required.
- Tests require real provider keys for baseline validation.
- Executor output includes private logs, secrets, or unapproved files.
- The task is not PRet-a-Coder.

## Acceptance Criteria

- PR004 is recorded as merged/done in all tracked surfaces.
- PR005 smoke coverage is present and no-key.
- Surface status is explicit for manifest, GitHub, and Vibe Kanban.
- Lane contracts define Codex and Cursor authority boundaries.
- Local no-secret validation is documented and runnable.
