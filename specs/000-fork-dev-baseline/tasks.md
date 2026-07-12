# Tasks: Fork Dev Baseline

**Input**: Design documents from `specs/000-fork-dev-baseline/`

**Prerequisites**: `plan.md`, `spec.md`

## Phase 1: Setup

- [x] T001 [P] Initialize Spec Kit project files under `.specify/`.
- [x] T002 [P] Update `.gitignore` so Spec Kit and tests can be committed while private run outputs stay ignored.
- [x] T003 [P] Add ChatIndex constitution in `.specify/memory/constitution.md`.

## Phase 2: Planning Contract

- [x] T004 [P] Record PR 0 objective and gates in repo-local planning docs.
- [x] T005 [P] Record canonical baseline workflow state in repo-local planning docs.
- [x] T006 [P] Add PR 0 task details to the baseline task list.
- [x] T007 [P] Record GitHub and external planning surface expectations when available.
- [x] T008 [P] Record implementation and review lane expectations.

## Phase 3: Baseline Validation

- [x] T009 Add no-secret baseline tests under `tests/`.
- [x] T010 Run local validation with project dependencies installed.
- [ ] T011 Record validation evidence in the PR body or final debrief.

## Phase 4: External Surface Gates

- [ ] T012 Verify or create `fr-meyer/ChatIndex`.
- [ ] T013 Authenticate `gh` with repo/project scopes on the runtime that will publish PR 0.
- [ ] T014 Create/sync fork `dev` from upstream `VectifyAI/ChatIndex@main`.
- [ ] T015 Create GitHub Issue and project-board item for PR 0.
- [ ] T016 Start or connect the matching external planning workspace if used.

## Phase 5: Executor and Review

- [ ] T017 Pass PRet-a-Coder gate once external publication/surface gates are ready.
- [ ] T018 Run maintainer baseline/review lane.
- [ ] T019 Run accepted implementation lane if code changes are required.
- [ ] T020 Run local review loop: inspect, test, fix, verify, accept/reject.
- [ ] T021 Commit/push/open PR only after explicit approval.

## Dependencies

- T009-T011 depend on T001-T008.
- T012-T016 require GitHub/planning-surface availability.
- T017 depends on baseline validation and required external gates.
- T018-T021 depend on T017.
