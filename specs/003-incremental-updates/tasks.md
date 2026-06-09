# Tasks: Incremental Updates

**Input**: `specs/003-incremental-updates/spec.md` and `plan.md`

## Phase 1: PRet-a-Coder Gate

- [x] T001 Confirm PR003 GitHub issue #9 exists.
- [x] T002 Add PR003 issue #9 to GitHub Project #1.
- [x] T003 Create Vibe local task for PR003.
- [x] T004 Confirm write scope: `ctree/`, `tests/`, `README.md`, `specs/003-incremental-updates/`, and `.speculoos/` metadata.
- [x] T005 Confirm tests must not use live provider keys.
- [x] T006 Confirm Cursor worker is the first implementation executor lane.

## Phase 2: Cursor Worker Implementation

- [x] T007 Prepare one-shot Cursor worker job with bounded prompt and acceptance criteria.
- [x] T008 Run Cursor worker against `feat/incremental-updates`.
- [x] T009 Inspect Cursor worker logs, result metadata, and changed files.

## Phase 3: Implementation Review

- [x] T010 Verify append-after-load behavior.
- [x] T011 Verify message index continuity.
- [x] T012 Verify current-node preservation.
- [x] T013 Verify localized reorganization behavior.
- [x] T014 Update README roadmap item after implementation is accepted.

## Phase 4: Validation

- [x] T015 Run unit tests.
- [x] T016 Run Python compile check.
- [x] T017 Run YAML parse check.
- [x] T018 Run `git diff --check`.
- [x] T019 Run Speculoos preflight.
- [x] T020 Run private-data/path scans.

## Phase 5: PR

- [ ] T021 Push branch to fork.
- [ ] T022 Open PR against fork `dev`.
- [ ] T023 Add PR to GitHub Project #1.
- [ ] T024 Move GitHub Project and Vibe task to review state.
