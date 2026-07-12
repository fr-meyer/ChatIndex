# Implementation Plan: Multi-LLM Support

**Branch**: `feat/multi-llm-support` | **Date**: 2026-06-08 | **Spec**: `specs/001-multi-llm-support/spec.md`

## Summary

Introduce a small provider abstraction for retrieval so `query_ctree` and
`query_ctree_streaming` can choose provider/model explicitly and be tested with
fake clients. Keep the first implementation narrow and compatible with the
current Anthropic retrieval path.

## Technical Context

**Language/Version**: Python 3.11 locally; project supports Python >=3.8.

**Primary Dependencies**: `openai`, `anthropic`, `python-dotenv`.

**Current Provider Coupling**:

- `ctree/utils.py` wraps OpenAI chat completions through `ChatGPT_API`.
- `ctree/ctree.py` calls `ChatGPT_API` for tree-building LLM operations.
- `retrieval/llm_tools.py` imports `Anthropic`, creates the client directly,
  and hardcodes `claude-sonnet-4-5` in non-streaming and streaming retrieval.

**Testing**: `python -m unittest discover -v`; new tests should use fake
clients and no provider keys.

**Target Platform**: Linux/GCP OpenClaw runtime, GitHub fork PR to `dev`.

**Constraints**: No real provider keys, `.env`, private OpenClaw logs, raw
sessions, or executor run payloads in the repository.

## Proposed Scope

### In Scope

- Provider/model config object or simple typed dictionary for retrieval.
- Dependency injection seam for retrieval client creation.
- Fake-client tests for provider/model selection and unsupported providers.
- README/quickstart note if public call shape changes or adds parameters.

### Out of Scope

- Full tree-building provider rewrite unless the implementation stays tiny.
- Live OpenAI/Anthropic integration tests.
- Vector search, incremental updates, or offline tree optimization.
- Any autonomous PR merge/publish by executor lanes.

## PRet-a-Coder Gate

Before implementation starts:

- Spec and plan are reviewed.
- Write scope is accepted.
- Test command is known.
- Implementation prompt and stop conditions are explicit.
- GitHub PR targets fork `dev`.
- Private-data review is required before merge.

## Expected Files

```text
retrieval/llm_tools.py
tests/test_multi_llm_support.py
README.md
```

Tree-building files (`ctree/utils.py`, `ctree/ctree.py`) are allowed only if the
implementation needs a shared provider config type and stays small.

## Validation

```bash
python -m unittest discover -v
git diff --check
```

Add a private-data scan before publish/merge.
