# Implementation Plan: Fork Dev Baseline

**Branch**: `chore/fork-dev-baseline` | **Date**: 2026-06-05 | **Spec**: `specs/000-fork-dev-baseline/spec.md`

**Input**: Feature specification from `specs/000-fork-dev-baseline/spec.md`

## Summary

Create the first ChatIndex fork baseline. The branch adds Spec Kit project
structure, repo-local planning notes, explicit surface expectations, executor
authority boundaries, and a no-secret baseline validation path for later roadmap
PRs.

## Technical Context

**Language/Version**: Python 3.11 locally; project supports Python >=3.8.

**Primary Dependencies**: `openai`, `anthropic`, `python-dotenv` from
`requirements.txt`.

**Storage**: Repository files only for committed workflow state. Private run
logs stay outside the repository.

**Testing**: `python -m unittest discover -v`; later PRs may add a stricter
test runner if needed.

**Target Platform**: Linux/GCP OpenClaw runtime, with GitHub fork/PR workflow.

**Project Type**: Python library/research prototype with repo-local planning
metadata.

**Performance Goals**: Not applicable for PR 0; correctness and reproducibility
come first.

**Constraints**: No real provider keys required for committed tests. No private
OpenClaw sessions or executor run payloads committed.

**Scale/Scope**: PR 0 scaffolds baseline workflow only. Roadmap features remain
future PRs.

## Constitution Check

- Lossless conversation provenance: satisfied; PR 0 does not alter retrieval
  behavior.
- Provider portability: satisfied by requiring fake/no-key validation.
- Testable before external calls: required before PR 0 acceptance.
- Small PRs with reviewable artifacts: satisfied by one branch for baseline.
- Private data stays out: enforced through `.gitignore` and lane contracts.

## Project Structure

### Documentation

```text
specs/000-fork-dev-baseline/
├── spec.md
├── plan.md
├── research.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
ctree/
retrieval/
tests/
```

**Structure Decision**: Keep Spec Kit and planning state repo-local. Add tests
under `tests/` once the baseline validation fixture is implemented.

## Complexity Tracking

No constitution violations expected for PR 0.
