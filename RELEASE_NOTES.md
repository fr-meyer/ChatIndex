# Release Notes

## v0.1.2 - 2026-06-14

Sandbox-provider and bounded-retrieval maintenance release.

This release promotes the PR018-PR020 batch from `dev` to `main`. It keeps
ChatIndex pre-1.0 while making OpenAI-compatible gateways easier to dogfood,
adding guardrails for longer tree builds, and making status-style retrieval
answers clearer when they come from a bounded or stale slice.

### Highlights

- Added OpenAI-compatible provider routing for CTree build and retrieval, with
  configurable base URLs, provider credentials, model IDs, request timeouts, and
  retry limits.
- Hardened compatible-provider JSON parsing for `null` parent indices returned
  by non-OpenAI models.
- Added build timeout/progress guardrails, bounded checkpoint save behavior, and
  source/provenance metadata for dogfood retrieval runs.
- Added freshness warnings for status-sensitive questions such as "what
  remains", "what is left", "next steps", and "current status".
- Documented bounded dogfood guidance for OpenAI-compatible gateways such as
  LiteLLM, Qwen-compatible endpoints, and Mistral-compatible routes.
- Cleaned trailing whitespace so release diff checks pass cleanly.

### Validation

- Unit tests: `.venv/bin/python -m unittest discover -v`
- Python syntax parse over tracked source and test files.
- YAML syntax parse over tracked workflow and metadata files.
- `git diff --check`
- Speculoos validation and release-plan dry run for the promotion task.

### Known Limitations

- The API remains pre-1.0 and may still change.
- Full-thread hosted-model builds can still be slow or expensive; bounded
  slices remain the recommended dogfood path.
- Branch protection and release immutability rules are not yet enabled.
- The package metadata is still split between `setup.py` and minimal
  `pyproject.toml` build-system metadata.

## v0.1.1 - 2026-06-12

Maintenance release for the post-v0.1.0 ChatIndex fork work.

This release promotes the current `dev` maintenance batch to `main`, preserving
the native Pullfrog workflow that is already on `main` while publishing the
runtime hardening fixes from `dev`.

### Highlights

- Hardened JSON extraction with an `ast.literal_eval` fallback for Python-style
  literals and expanded extraction tests.
- Rejected negative `node_path` entries in `view_node_and_children` before
  Python negative-list indexing can select unintended children.
- Documented the Speculoos `release-plan` helper for future release-gated work.
- Documented the CodeRabbit caveat for PRs targeting the non-default `dev`
  branch.
- Preserved the native Pullfrog review workflow on `main`.

### Validation

- Unit tests: `.venv/bin/python -m unittest discover -v`
- Python syntax parse over tracked source and test files.
- YAML syntax parse over tracked workflow and metadata files.
- `git diff --check`
- Speculoos validation and release-plan dry run for the promotion task.

### Known Limitations

- The API remains pre-1.0 and may still change.
- Branch protection and release immutability rules are not yet enabled.
- The package metadata is still split between `setup.py` and minimal
  `pyproject.toml` build-system metadata.

## v0.1.0 - 2026-06-11

Initial beta release of the ChatIndex fork.

This release promotes the current `dev` branch work as the first stable branch
publication point for the fork. The package version remains `0.1.0` because the
public API is still pre-1.0, but the project maturity moves from alpha to beta:
the initial roadmap items are implemented and covered by local unit/smoke tests,
while future compatibility guarantees still need to be defined before `v1.0.0`.

### Highlights

- Added retrieval provider selection for Anthropic and OpenAI-backed retrieval.
- Added offline tree reorganization optimization.
- Added incremental CTree update support.
- Added vector-search-backed retrieval helpers.
- Added end-to-end smoke coverage and expanded unit tests.
- Cleaned README install instructions and package metadata.
- Added minimal PEP 517 build-system metadata.
- Added Speculoos workflow artifacts used to coordinate the implementation loop.

### Validation

- Unit tests: `.venv/bin/python -m unittest discover -v`
- Python syntax parse over tracked source and test files.
- YAML syntax parse over tracked workflow and metadata files.
- `git diff --check`
- Speculoos validation for the release-prep task.

### Known Limitations

- The API remains pre-1.0 and may still change.
- The release/tag publication flow is still manual and confirmation-gated.
- Branch protection and release immutability rules are not yet enabled.
- The package metadata is still split between `setup.py` and minimal
  `pyproject.toml` build-system metadata.
