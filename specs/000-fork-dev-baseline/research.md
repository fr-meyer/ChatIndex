# Research: Fork Dev Baseline

## Decision: Repo-local workflow state

Committed project notes store workflow state so the branch can be reviewed
without private OpenClaw logs.

**Rationale**: The fork should carry enough state to reconstruct task readiness,
surface mappings, and authority boundaries from Git alone.

**Alternatives considered**:

- OpenClaw memory only: rejected because reviewers cannot see the workflow
  contract from the PR.
- GitHub Issues only: rejected because it does not describe executor lane
  contracts or local run artifacts.

## Decision: Additive task surfaces

The canonical v0 state is the local project note, while GitHub Issues, project
boards, and optional planning workspaces can mirror task state when available.

**Rationale**: Different surfaces are useful for different roles. The manifest
remains available even when external auth or services are blocked.

## Decision: No-secret validation

PR 0 must be validatable without real API keys.

**Rationale**: Provider keys are sensitive and should not be required for CI or
basic repository health checks.
