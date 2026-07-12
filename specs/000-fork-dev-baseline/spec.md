# Feature Specification: Fork Dev Baseline

**Feature Branch**: `chore/fork-dev-baseline`

**Created**: 2026-06-05

**Status**: Draft

**Input**: Establish the first ChatIndex fork baseline PR.

## User Scenarios & Testing

### User Story 1 - Reproducible Fork Baseline (Priority: P1)

As a maintainer, I can clone the fork, install dependencies, and run a local
validation command without real API keys.

**Why this priority**: Every later roadmap PR depends on a dependable baseline.

**Independent Test**: A fresh checkout runs the documented validation command
and passes with fake/no-key test paths.

**Acceptance Scenarios**:

1. **Given** a fresh clone, **When** dependencies are installed, **Then** local
   tests run without provider keys.
2. **Given** no `.env` file, **When** the baseline tests run, **Then** tests do
   not attempt live OpenAI or Anthropic calls.

---

### User Story 2 - Reviewable Planning State (Priority: P1)

As an operator, I can inspect the PR 0 goal, task status, external surface
expectations, and executor authority boundaries from committed repo-local files.

**Why this priority**: The dogfood workflow needs durable state that does not
depend on a single chat transcript.

**Independent Test**: Inspect the fork baseline spec, plan, tasks, and project
documentation.

**Acceptance Scenarios**:

1. **Given** the PR 0 branch, **When** I open the repo-local planning files,
   **Then** I can see branch, base, task, lane, and gate status.
2. **Given** external surfaces are unavailable, **When** I inspect
   the project notes, **Then** blocked/pending states and required next actions
   are explicit.

---

### User Story 3 - Safe Executor Handoff (Priority: P2)

As an operator, I can hand the PR 0 task to a bounded executor lane only after
the PRet-a-Coder gate passes.

**Why this priority**: Executor work must be isolated, logged, and reviewable.

**Independent Test**: The PR 0 task file and lane contracts list the required
preconditions before code changes are allowed.

**Acceptance Scenarios**:

1. **Given** GitHub auth or the fork is missing, **When** the PRet-a-Coder gate
   is evaluated, **Then** the task remains blocked from publish/PR actions.
2. **Given** an executor produces changes, **When** OpenClaw reviews the result,
   **Then** logs, changed files, tests, and acceptance status are available.

## Edge Cases

- Fork repository is not visible or does not exist yet.
- GitHub CLI is installed but unauthenticated.
- An external planning workspace is unavailable or not connected yet.
- Docker is unavailable from the current OpenClaw container.
- A dependency install succeeds but live provider keys are absent.

## Requirements

### Functional Requirements

- **FR-001**: The branch MUST contain Spec Kit project artifacts under
  `.specify/`.
- **FR-002**: The branch MUST contain repo-local planning notes for PR 0.
- **FR-003**: The planning notes MUST identify canonical, GitHub, and external
  planning expectations separately when those surfaces are used.
- **FR-004**: The PR 0 task MUST remain blocked from publish/PR actions until
  fork visibility, GitHub auth, and human approval gates are satisfied.
- **FR-005**: Runtime logs and private run payloads MUST NOT be committed.
- **FR-006**: Baseline validation MUST be possible without real provider keys.

### Key Entities

- **ProjectPlan**: Repo-local workflow state for project, branch, surfaces,
  lanes, gates, and current task.
- **TaskPlan**: Task-level readiness, acceptance criteria, executor assignment,
  and gate state.
- **SurfaceMapping**: External IDs/URLs/status for GitHub Issues, project
  boards, and optional planning workspaces.
- **LaneContract**: Bounded executor permissions, required outputs, and review
  expectations.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A reviewer can identify the PR 0 objective, status, blockers, and
  next actions from repo files alone.
- **SC-002**: A no-secret local validation command is documented and runnable.
- **SC-003**: External surface states are explicit even when they are blocked or
  pending.
- **SC-004**: Executor authority boundaries are visible before any executor
  edits code.

## Assumptions

- The fork will be owned by `fr-meyer/ChatIndex` once available.
- The fork `dev` branch will track upstream `VectifyAI/ChatIndex@main`.
- ChatIndex baseline tests should use fake providers by default.
- OpenClaw keeps private runtime logs outside this repository.
