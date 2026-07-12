# Tasks: Multi-LLM Support

**Input**: `specs/001-multi-llm-support/spec.md` and `plan.md`

## Phase 1: Spec Review

- [x] T001 [P] Create PR001 spec, plan, research, quickstart, and task list.
- [x] T002 [P] Record GitHub Issue blocker because Issues are disabled on the fork.
- [x] T003 [P] Verify external planning task availability.
- [x] T004 Review and accept PR001 scope before implementation.

## Phase 2: PRet-a-Coder Gate

- [x] T005 Confirm write scope for retrieval, tests, docs, and planning docs.
- [x] T006 Confirm credential policy: fake-client tests only; no committed provider keys or `.env`.
- [x] T007 Confirm executor lane: maintainer implements directly for this v0 pass after approval.
- [x] T008 Confirm stop conditions and validation commands.

## Phase 3: Implementation

- [x] T009 Add retrieval provider/model configuration seam.
- [x] T010 Preserve existing Anthropic default behavior.
- [x] T011 Add fake-client tests for provider selection and unsupported provider errors.
- [x] T012 Update README/quickstart documentation if public usage changes.

## Phase 4: Review and Merge

- [x] T013 Run `.venv/bin/python -m unittest discover -v`.
- [x] T014 Run `git diff --check`.
- [x] T015 Run private-data scan before PR publication and before merge.
- [x] T016 Maintainer review signoff.
- [ ] T017 Merge only after gates are recorded.

## Dependencies

- T004-T008 must pass before Cursor implementation starts.
- T013-T016 must pass before merge.
