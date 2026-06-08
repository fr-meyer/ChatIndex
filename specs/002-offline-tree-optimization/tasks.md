# Tasks: Offline Tree Optimization

**Input**: `specs/002-offline-tree-optimization/spec.md` and `plan.md`

## Phase 1: PRet-a-Coder Gate

- [x] T001 Confirm PR002 GitHub issue #7 and Project #1 item exist.
- [x] T002 Confirm Vibe local task exists for PR002.
- [x] T003 Confirm write scope: `ctree/`, `tests/`, `specs/002-offline-tree-optimization/`, and `.speculoos/` metadata.
- [x] T004 Confirm tests must not use live provider keys.

## Phase 2: Implementation

- [x] T005 Optimize ancestor list construction without changing order.
- [x] T006 Make CTree add-path reorganization path-local.
- [x] T007 Keep explicit full-tree reorganization available.
- [x] T008 Recheck parents after child expansion/split.

## Phase 3: Tests

- [x] T009 Add no-key tests for ancestor order.
- [x] T010 Add no-key test that unrelated overflowing branches are ignored by path-local checks.
- [x] T011 Add no-key test that parent overflow is rechecked after child split.

## Phase 4: Review

- [x] T012 Run unit tests.
- [x] T013 Run Python compile check.
- [x] T014 Run `git diff --check`.
- [x] T015 Run Speculoos preflight.
- [ ] T016 Open PR against fork `dev`.
