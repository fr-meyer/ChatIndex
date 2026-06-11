# Feature Specification: End-to-End Smoke and Speculoos Closure

**Feature Branch**: `feat/e2e-smoke-speculoos-closure`

**Created**: 2026-06-09

**Status**: Draft

**Input**: PR005 issue #13, "End-to-end smoke and Speculoos closure".

## User Scenarios & Testing

### User Story 1 - Prove Roadmap Features Compose (Priority: P1)

As a ChatIndex maintainer, I can run one no-key smoke test that builds a CTree,
saves it, loads it, appends a new exchange, vector-searches for that appended
content, and retrieves the returned message range.

**Why this priority**: PR001-PR004 validated pieces independently. The closure
slice should prove the merged retrieval, incremental update, and vector-search
paths work together.

**Independent Test**: A unit test uses stubbed LLM helpers and a temporary file
to exercise build/save/load/append/vector-search/get-messages without provider
keys or network calls.

### User Story 2 - Keep Speculoos State Honest (Priority: P1)

As a maintainer, the repo-local Speculoos metadata reflects that PR004 is merged
and PR005 is the current hardening slice.

**Why this priority**: The Plancha surface is only useful if GitHub, Vibe, and
repo-local status agree.

**Independent Test**: YAML parsing succeeds and the status files identify PR005
as the active task while retaining PR004 as done.

## Requirements

- **FR-001**: PR005 MUST add no-key smoke coverage for build/save/load/append
  plus vector retrieval over the appended exchange.
- **FR-002**: The smoke test MUST use stubbed LLM methods and MUST NOT require
  `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, provider network access, or external
  vector databases.
- **FR-003**: The smoke test MUST verify that `vector_search` result ranges can
  be passed to `get_node_messages` to recover the raw conversation slice.
- **FR-004**: Speculoos metadata MUST record PR004 as done and PR005 as the
  active slice.
- **FR-005**: PR005 MUST NOT commit generated tree files, vector index files,
  provider keys, `.env` files, private logs, raw sessions, or OpenClaw private
  state.

## Success Criteria

- **SC-001**: Existing no-key unit tests pass.
- **SC-002**: New no-key smoke test covers the composed ChatIndex path.
- **SC-003**: YAML parse and Speculoos preflight pass.
- **SC-004**: GitHub Project and Vibe surfaces are synchronized for PR005.

## Non-Goals

- No new retrieval provider abstraction.
- No production vector database or embedding-provider integration.
- No performance benchmark or live LLM benchmark.
- No promotion from fork `dev` to `main`.
