# Implementation Plan: Offline Tree Optimization

**Branch**: `feat/offline-tree-path-reorg` | **Date**: 2026-06-08 | **Spec**: `specs/002-offline-tree-optimization/spec.md`

## Summary

Optimize incremental CTree construction by checking overflow only on the topic
path touched by the newly added exchange. Preserve the existing full-tree
reorganization helper for explicit internal use.

## Technical Context

**Language/Version**: Python 3.11 locally; project supports Python >=3.8.

**Primary Dependencies**: Existing `openai`, `anthropic`, and `python-dotenv`.

**Testing**: `.venv/bin/python -m unittest discover -v`.

**Performance Goal**: Avoid full-tree traversal after every `CTree.add()` when
only the changed topic path can have new overflow.

**Constraints**: No live API calls in tests; no tree JSON format change.

## Implementation

- Replace repeated ancestor front-insertion with append/reverse.
- Add a small helper that determines a single node's reorganization action.
- Make `_check_and_reorganize_nodes(start_node=...)` walk from the changed
  topic to the root, applying expansion/split and rechecking parents.
- Keep `_check_and_reorganize_nodes()` without `start_node` as a full-tree scan.
- Add focused tests for ordering, unrelated overflow, and parent recheck.

## Validation

- `.venv/bin/python -m unittest discover -v`
- `.venv/bin/python -m py_compile ctree/ctree.py tests/test_offline_tree_optimization.py`
- `git diff --check`
- Local preflight checklist
