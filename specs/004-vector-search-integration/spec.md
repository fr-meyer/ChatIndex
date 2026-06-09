# Feature Specification: Vector Search Integration

**Feature Branch**: `feat/vector-search-integration`

**Created**: 2026-06-09

**Status**: Draft

**Input**: PR004 issue #11, "Vector search integration".

## User Scenarios & Testing

### User Story 1 - Find Relevant Messages by Similarity (Priority: P1)

As a ChatIndex maintainer, I can build a deterministic no-key vector index over
stored conversation exchanges and search it with a natural-language query.

**Why this priority**: Vector search gives retrieval a fast candidate generator
when the tree summary alone does not point clearly to the relevant branch.

**Independent Test**: A no-key unit test builds a vector index from a small
conversation, searches for a query, and verifies the most relevant exchange is
ranked first with message index, score, preview, and message range metadata.

### User Story 2 - Keep Tree Navigation as the Primary Structure (Priority: P1)

As a retrieval caller, I can still use `view_node_and_children` and
`get_node_messages` exactly as before, with vector search added as an optional
tool rather than a replacement.

**Why this priority**: ChatIndex is tree-first. PR004 should broaden retrieval,
not change existing public call shapes.

**Independent Test**: Existing retrieval-loop tests continue to pass, and a
new tool-loop test calls `vector_search` through `query_ctree` without API keys.

### User Story 3 - Rebuild Vector Indexes Safely (Priority: P2)

As a maintainer, I can reconstruct the vector index from the saved CTree
conversation data instead of committing generated index artifacts.

**Why this priority**: Generated vector dumps are derived data and can contain
private conversation text. They should not enter the repository.

**Independent Test**: Unit tests construct the index in memory from the tree and
do not read or write `.index`, `.faiss`, or external provider files.

## Requirements

- **FR-001**: Retrieval MUST provide a deterministic no-key embedding path for
  tests and local validation.
- **FR-002**: The vector index MUST index user/assistant exchanges with
  `message_index`, message range, source text, and preview metadata.
- **FR-003**: The nearest-neighbor search API MUST bound `top_k` and return
  stable ranked results with numeric similarity scores.
- **FR-004**: `ChatIndexTools` MUST expose vector search as an additive retrieval
  tool without breaking `view_node_and_children` or `get_node_messages`.
- **FR-005**: Vector-search results MUST include enough metadata for callers to
  fetch the raw conversation range with `get_node_messages`.
- **FR-006**: PR004 MUST NOT commit generated vector index files, real provider
  keys, `.env` files, private logs, raw sessions, or OpenClaw private state.

## Success Criteria

- **SC-001**: Existing no-key unit tests pass.
- **SC-002**: New no-key unit tests cover deterministic vector indexing and
  nearest-neighbor ranking.
- **SC-003**: New no-key unit tests cover `vector_search` through the retrieval
  tool loop.
- **SC-004**: README roadmap marks vector search integration complete after the
  implementation is accepted.

## Non-Goals

- No production FAISS, Chroma, Qdrant, or other vector database dependency in
  PR004.
- No mandatory live embedding-provider key or network call.
- No semantic change to CTree construction or tree navigation.
- No generated vector-index artifact committed to the repository.
- No merge to `main`; PR004 targets fork `dev`.
