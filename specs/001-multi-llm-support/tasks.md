# Tasks: Multi-LLM Support

**Input**: `specs/001-multi-llm-support/spec.md` and `plan.md`

## Phase 1: Spec Review

- [x] T001 [P] Create PR001 spec, plan, research, quickstart, and task list.
- [x] T002 [P] Record GitHub Issue blocker because Issues are disabled on the fork.
- [x] T003 [P] Verify Vibe Kanban MCP command availability through `npx`; MCP binary is present but requires the main Vibe Kanban app/service to be running.
- [ ] T004 Review and accept PR001 scope before implementation.

## Phase 2: PRet-a-Coder Gate

- [ ] T005 Confirm write scope for retrieval, tests, docs, and Speculoos task state.
- [ ] T006 Confirm credential policy: fake-client tests only; no committed provider keys or `.env`.
- [ ] T007 Confirm executor lane: Cursor worker may implement after Codex reviews this spec.
- [ ] T008 Confirm stop conditions and validation commands.

## Phase 3: Implementation

- [ ] T009 Add retrieval provider/model configuration seam.
- [ ] T010 Preserve existing Anthropic default behavior.
- [ ] T011 Add fake-client tests for provider selection and unsupported provider errors.
- [ ] T012 Update README/quickstart documentation if public usage changes.

## Phase 4: Review and Merge

- [ ] T013 Run `python -m unittest discover -v`.
- [ ] T014 Run `git diff --check`.
- [ ] T015 Run private-data scan before PR publication and before merge.
- [ ] T016 Codex review signoff.
- [ ] T017 Merge only after gates are recorded.

## Dependencies

- T004-T008 must pass before Cursor implementation starts.
- T013-T016 must pass before merge.
