# Feature Specification: Incremental Updates

**Feature Branch**: `feat/incremental-updates`

**Created**: 2026-06-09

**Status**: Draft

**Input**: PR003 issue #9, "Incremental updates".

## User Scenarios & Testing

### User Story 1 - Append to a Saved Tree (Priority: P1)

As a ChatIndex maintainer, I can load a saved CTree and append new
user/assistant exchanges without rebuilding the index from scratch.

**Why this priority**: Conversations are dynamic. A long-running conversation
index must continue from its saved state.

**Independent Test**: A no-key unit test loads a saved tree, appends exchanges,
and verifies message indexes continue after the existing conversation length.

### User Story 2 - Preserve Current Topic State (Priority: P1)

As a ChatIndex maintainer, appending to a loaded tree continues from the
restored current topic rather than resetting to the root.

**Why this priority**: Incremental updates must preserve temporal continuity
and avoid disturbing older frozen structure.

**Independent Test**: A no-key unit test verifies `current_node` after load,
then appends an exchange and confirms the new message is added beneath the
restored current path.

### User Story 3 - Local Reorganization Only (Priority: P2)

As a ChatIndex maintainer, incremental appends trigger only the affected
reorganization path when a topic overflows.

**Why this priority**: PR002 made path-local checks available; PR003 should make
incremental updates rely on that behavior rather than a full rebuild.

**Independent Test**: A no-key unit test stubs LLM-dependent helpers and
verifies unrelated overflowing branches are not rebuilt during append.

## Requirements

- **FR-001**: `CTree.load()` followed by `CTree.add()` MUST append new exchanges
  after the saved conversation length.
- **FR-002**: Message indexes for appended exchanges MUST remain contiguous and
  stable after save/load roundtrips.
- **FR-003**: `current_node` MUST be restored from the loaded tree and used as
  the default append target.
- **FR-004**: Incremental appends MUST reuse path-local reorganization for the
  changed topic path.
- **FR-005**: Public `CTree.add()`, `CTree.save()`, and `CTree.load()` call
  shapes MUST remain backward compatible.
- **FR-006**: Tests MUST run without provider API keys or network calls.

## Success Criteria

- **SC-001**: Unit tests cover append-after-load and index continuity.
- **SC-002**: Unit tests cover current-node preservation across load and append.
- **SC-003**: Unit tests cover localized reorganization during append.
- **SC-004**: `python -m unittest discover -v` passes without live API keys.

## Non-Goals

- No vector search in PR003.
- No migration to a new saved tree JSON schema unless strictly optional and
  backward compatible.
- No live LLM benchmarks or provider-key validation.
