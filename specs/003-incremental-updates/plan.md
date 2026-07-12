# Implementation Plan: Incremental Updates

**Branch**: `feat/incremental-updates` | **Date**: 2026-06-09 | **Spec**: `specs/003-incremental-updates/spec.md`

## Summary

Implement a focused incremental-update pass for CTree so a saved or loaded tree
can accept appended user/assistant exchanges while preserving the current topic
path, stable message indexes, and path-local reorganization behavior.

## Technical Context

**Language/Version**: Python 3.11 locally; project supports Python >=3.8.

**Primary Dependencies**: Existing `openai`, `anthropic`, and `python-dotenv`.

**Testing**: `.venv/bin/python -m unittest discover -v`.

**Performance Goal**: Avoid rebuilding the full tree for appended conversation
messages.

**Constraints**: No live API calls in tests; public CTree call shapes stay
compatible; no committed secrets, private logs, sessions, or generated worker
artifacts.

## Implementation

- Review the existing add/load/save/current-node behavior and identify the
  minimal gap that blocks append-after-load behavior.
- Add or adjust helper behavior only where it improves append clarity.
- Preserve existing saved JSON compatibility.
- Add no-key tests using stubbed LLM helpers rather than provider calls.
- Mark README roadmap item complete only after implementation and validation.

## Implementation Lane

The implementation lane should attempt the first pass within the allowed write
scope. Maintainer review remains responsible for reviewing the diff, running
tests, fixing issues, publishing, PR creation, project status, merge
recommendation, and follow-up notes.

## Validation

- `.venv/bin/python -m unittest discover -v`
- `.venv/bin/python -m py_compile ctree/ctree.py tests/test_incremental_updates.py`
- YAML parse check for tracked workflow files when present
- `git diff --check`
- Local preflight checklist
- Secret/path scans over the diff before publication
