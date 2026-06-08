# Goal: ChatIndex Fork PR 0 Baseline

## Objective

Create the first ChatIndex fork baseline branch through Speculoos v0 so later
roadmap PRs can use a repeatable spec, task, executor, review, and PR workflow.

## Scope

- Initialize Spec Kit artifacts.
- Add repo-local Speculoos workflow state.
- Define task surfaces and executor authority boundaries.
- Establish a no-secret validation path.
- Prepare for fork `dev` and PR 0 publication once GitHub auth/fork access is
  available.

## Non-goals

- Implement multi-LLM support.
- Implement offline tree optimization.
- Implement incremental updates.
- Implement vector search.
- Commit private OpenClaw logs or real provider responses.

## Stop Conditions

- Fork visibility or GitHub auth is missing when a publish action is required.
- Tests require real provider keys for baseline validation.
- Executor output includes private logs, secrets, or unapproved files.
- The task is not PRet-a-Coder.

## Acceptance Criteria

- Spec Kit and Speculoos files are present and reviewable.
- Surface status is explicit for manifest, GitHub, and Vibe Kanban.
- Lane contracts define Codex and Cursor authority boundaries.
- Local no-secret validation is documented and runnable.
- Commit/push/PR actions remain blocked until explicit approval.
