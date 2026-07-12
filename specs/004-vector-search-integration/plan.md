# Implementation Plan: Vector Search Integration

PR004 adds a small, no-key vector-search layer for retrieval tools. The first
implementation should be deterministic, in-memory, and easy to test.

## Proposed Design

- Add a retrieval-side vector index module or classes near the existing
  retrieval tool code.
- Represent each indexed exchange with `message_index`, source text, previews,
  message range, and vector.
- Provide a deterministic local embedding implementation for tests and local
  validation. It should not require provider keys or network access.
- Use cosine similarity or an equivalent normalized dot-product score for
  nearest-neighbor search.
- Add a `vector_search` retrieval tool exposed through `ChatIndexTools` and the
  shared tool list used by `query_ctree` and `query_ctree_streaming`.
- Keep existing `ChatIndexTools`, `query_ctree`, and provider call shapes
  backward compatible.

## Validation

- `.venv/bin/python -m unittest discover -v`
- `.venv/bin/python -m py_compile retrieval/llm_tools.py`
- YAML parse check for tracked workflow files when present
- `git diff --check`
- Local preflight checklist

## Executor

The implementation executor lane makes the first pass. Maintainer review patches
if needed, validates, updates surfaces, and opens the PR.
