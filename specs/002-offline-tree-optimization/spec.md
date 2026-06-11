# Feature Specification: Offline Tree Optimization

**Feature Branch**: `feat/offline-tree-path-reorg`

**Created**: 2026-06-08

**Status**: Draft

**Input**: PR002 issue #7, "Offline tree optimization".

## User Scenarios & Testing

### User Story 1 - Path-Local Reorganization (Priority: P1)

As a ChatIndex maintainer, I can add a conversation exchange without scanning
every tree node for overflow after each insert.

**Why this priority**: Incremental offline tree construction should scale with
the path touched by the new exchange, not with the whole tree size.

**Independent Test**: A no-key unit test verifies that path-local
reorganization ignores an unrelated overflowing branch.

### User Story 2 - Parent Recheck After Split (Priority: P1)

As a ChatIndex maintainer, I still get correct overflow handling when a child
split increases the direct child count of its parent.

**Why this priority**: The optimization must not skip parent overflow created
by a child reorganization.

**Independent Test**: A no-key unit test stubs splitting and verifies that the
changed node and then its parent are checked in order.

### User Story 3 - Ancestor Lookup Stability (Priority: P2)

As a retrieval/tree maintainer, ancestor lookups keep the same root-to-leaf
ordering while avoiding repeated front-list insertion.

**Independent Test**: A no-key unit test checks include/exclude-root behavior
and ordering.

## Requirements

- **FR-001**: `CTree.add()` MUST limit overflow checks to the changed topic and
  its ancestors.
- **FR-002**: Full-tree overflow checking MUST remain available for explicit
  internal calls that do not pass a start node.
- **FR-003**: Parent nodes MUST be rechecked after child expansion or split.
- **FR-004**: Tests MUST run without provider API keys or network calls.
- **FR-005**: Public CTree add/load/save call shapes MUST remain compatible.

## Success Criteria

- **SC-001**: Unit tests cover path-local reorganization and parent recheck.
- **SC-002**: Existing retrieval provider tests still pass.
- **SC-003**: `python -m unittest discover -v` passes without live API keys.

## Non-Goals

- No provider abstraction for tree-building in PR002.
- No live benchmark requiring provider credentials.
- No changes to saved tree JSON format.
