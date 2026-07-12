# Tasks: End-to-End Smoke

**Input**: `specs/005-e2e-smoke/spec.md` and `plan.md`

## Phase 1: PRet-a-Coder Gate

- [x] T001 Confirm PR005 GitHub issue #13 exists.
- [x] T002 Add PR005 issue #13 to the project board.
- [x] T003 Create local planning task for PR005.
- [x] T004 Confirm write scope: `tests/`, `README.md`, and `specs/005-e2e-smoke/`.
- [x] T005 Confirm tests must not use live provider keys.
- [x] T006 Confirm the first implementation executor lane.

## Phase 2: Cursor Worker Implementation

- [x] T007 Prepare one-shot implementation job with bounded prompt and acceptance criteria.
- [x] T008 Run implementation lane against `feat/e2e-smoke`.
- [x] T009 Inspect implementation logs, result metadata, and changed files.

## Phase 3: Implementation Review

- [x] T010 Verify build/save/load/append smoke coverage.
- [x] T011 Verify vector result ranges retrieve raw messages.
- [x] T012 Verify project notes have PR004 done and PR005 active.
- [x] T013 Update README/docs if implementation warrants it.

## Phase 4: Validation

- [x] T014 Run unit tests.
- [x] T015 Run Python compile check.
- [x] T016 Run YAML parse check.
- [x] T017 Run `git diff --check`.
- [x] T018 Run local preflight.
- [x] T019 Run private-data/path scans.

## Phase 5: PR

- [x] T020 Push branch to fork.
- [x] T021 Open PR against fork `dev`.
- [x] T022 Add PR to the project board.
- [x] T023 Move project task to review state.
