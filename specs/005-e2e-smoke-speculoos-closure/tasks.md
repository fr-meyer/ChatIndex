# Tasks: End-to-End Smoke and Speculoos Closure

**Input**: `specs/005-e2e-smoke-speculoos-closure/spec.md` and `plan.md`

## Phase 1: PRet-a-Coder Gate

- [x] T001 Confirm PR005 GitHub issue #13 exists.
- [x] T002 Add PR005 issue #13 to GitHub Project #1.
- [x] T003 Create Vibe local task for PR005.
- [x] T004 Confirm write scope: `tests/`, `README.md`, `specs/005-e2e-smoke-speculoos-closure/`, and `.speculoos/` metadata.
- [x] T005 Confirm tests must not use live provider keys.
- [x] T006 Confirm Cursor worker is the first implementation executor lane.

## Phase 2: Cursor Worker Implementation

- [x] T007 Prepare one-shot Cursor worker job with bounded prompt and acceptance criteria.
- [x] T008 Run Cursor worker against `feat/e2e-smoke-speculoos-closure`.
- [x] T009 Inspect Cursor worker logs, result metadata, and changed files.

## Phase 3: Implementation Review

- [x] T010 Verify build/save/load/append smoke coverage.
- [x] T011 Verify vector result ranges retrieve raw messages.
- [x] T012 Verify Speculoos metadata has PR004 done and PR005 active.
- [x] T013 Update README/docs if implementation warrants it.

## Phase 4: Validation

- [x] T014 Run unit tests.
- [x] T015 Run Python compile check.
- [x] T016 Run YAML parse check.
- [x] T017 Run `git diff --check`.
- [x] T018 Run Speculoos preflight.
- [x] T019 Run private-data/path scans.

## Phase 5: PR

- [x] T020 Push branch to fork.
- [x] T021 Open PR against fork `dev`.
- [x] T022 Add PR to GitHub Project #1.
- [x] T023 Move GitHub Project and Vibe task to review state.
