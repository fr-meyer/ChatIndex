# Tasks: Fork Dev Baseline

**Input**: Design documents from `specs/000-fork-dev-baseline/`

**Prerequisites**: `plan.md`, `spec.md`

## Phase 1: Setup

- [x] T001 [P] Initialize Spec Kit project files under `.specify/`.
- [x] T002 [P] Update `.gitignore` so Spec Kit, Speculoos, and tests can be committed while private run outputs stay ignored.
- [x] T003 [P] Add ChatIndex constitution in `.specify/memory/constitution.md`.

## Phase 2: Speculoos Workflow Contract

- [x] T004 [P] Add `.speculoos/goal.md` for PR 0 objective and gates.
- [x] T005 [P] Add `.speculoos/manifest.yaml` as canonical v0 workflow state.
- [x] T006 [P] Add PR 0 task record in `.speculoos/tasks/pr-000-fork-dev-baseline.yaml`.
- [x] T007 [P] Add GitHub and Vibe Kanban surface mapping files under `.speculoos/surfaces/`.
- [x] T008 [P] Add Codex and Cursor lane contracts under `.speculoos/lane-contracts/`.

## Phase 3: Baseline Validation

- [x] T009 Add no-secret baseline tests under `tests/`.
- [x] T010 Run local validation with project dependencies installed.
- [ ] T011 Record validation evidence in the PR body or final debrief.

## Phase 4: External Surface Gates

- [ ] T012 Verify or create `fr-meyer/ChatIndex`.
- [ ] T013 Authenticate `gh` with repo/project scopes on the runtime that will publish PR 0.
- [ ] T014 Create/sync fork `dev` from upstream `VectifyAI/ChatIndex@main`.
- [ ] T015 Create GitHub Issue and GitHub Project item for PR 0.
- [ ] T016 Start or connect Vibe Kanban sidecar/MCP bridge and create the matching Vibe issue/workspace.

## Phase 5: Executor and Review

- [ ] T017 Pass PRet-a-Coder gate once external publication/surface gates are ready.
- [ ] T018 Run Codex baseline/review lane.
- [ ] T019 Run accepted Cursor worker lane if code changes are required.
- [ ] T020 Run Speculoos Loop: inspect, test, fix, verify, accept/reject.
- [ ] T021 Commit/push/open PR only after explicit approval.

## Dependencies

- T009-T011 depend on T001-T008.
- T012-T016 require GitHub/Vibe availability.
- T017 depends on baseline validation and required external gates.
- T018-T021 depend on T017.
