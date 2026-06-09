# Implementation Plan: End-to-End Smoke and Speculoos Closure

PR005 is a hardening slice after the README roadmap features are complete. It
should stay small: one composed no-key smoke test plus status/documentation
cleanup.

## Proposed Design

- Add a focused test module or test case under `tests/`.
- Build a `CTree` with `api_key="test-openai-key"` and stub all LLM-dependent
  methods used by `add`.
- Save to a temporary JSON file with conversation data, then reload with
  `CTree.load`.
- Append one additional exchange after load.
- Use `ChatIndexTools.vector_search` to find the appended exchange.
- Use the returned `start_index`/`end_index` with `get_node_messages` and assert
  the raw message content is recovered.
- Update Speculoos metadata so PR005 is active and PR004 is done.
- Keep the setup and implementation no-key, deterministic, and free of generated
  artifacts.

## Validation

- `.venv/bin/python -m unittest discover -v`
- `.venv/bin/python -m py_compile ctree/ctree.py retrieval/llm_tools.py retrieval/vector_index.py tests/test_e2e_smoke.py`
- `ruby -e "require 'yaml'; Dir['.speculoos/**/*.yaml'].each { |p| YAML.parse_file(p) }"`
- `git diff --check`
- `scripts/speculoos-chatindex-preflight /home/node/.openclaw/repos/ChatIndex`
- Secret/path scan over the PR005 diff.

## Executor

Cursor is the first implementation executor lane. Codex reviews, patches if
needed, validates, updates surfaces, and opens the PR.
