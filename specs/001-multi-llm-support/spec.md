# Feature Specification: Multi-LLM Support

**Feature Branch**: `feat/multi-llm-support`

**Created**: 2026-06-08

**Status**: Draft

**Input**: ChatIndex roadmap item "Multi-LLM support" and Speculoos PR001 dogfood.

## User Scenarios & Testing

### User Story 1 - Configurable Retrieval Provider (Priority: P1)

As a ChatIndex user, I can query a saved CTree with an explicit provider/model
configuration instead of relying on a hardcoded Anthropic model inside
`query_ctree`.

**Why this priority**: Retrieval is the user-facing roadmap item and currently
hardcodes `Anthropic` plus `claude-sonnet-4-5`.

**Independent Test**: A fake provider client can be injected into retrieval and
the retrieval loop can run without live API keys.

**Acceptance Scenarios**:

1. **Given** no provider API keys, **When** provider-selection tests run with a
   fake client, **Then** the tests pass without network calls.
2. **Given** an explicit provider/model config, **When** `query_ctree` starts,
   **Then** the selected provider/model is used instead of a hardcoded default.

---

### User Story 2 - Backward-Compatible Public API (Priority: P1)

As an existing user, I can keep calling `query_ctree(api_key=..., ctree=...,
user_query=...)` while the new provider configuration is introduced.

**Why this priority**: The first feature PR should be small and low-risk.

**Independent Test**: Existing import and call-shape tests still pass, and
backward-compatible defaults are documented.

**Acceptance Scenarios**:

1. **Given** existing code that passes an Anthropic key to `query_ctree`, **When**
   no provider is specified, **Then** the function keeps the current Anthropic
   behavior.
2. **Given** a caller passes an unsupported provider name, **When** retrieval is
   initialized, **Then** the error is clear and no live API call is attempted.

---

### User Story 3 - Tree-Build Provider Preparation (Priority: P2)

As a maintainer, I can see a clear extension path for tree-building provider
support, even if PR001 keeps the implementation focused on retrieval.

**Why this priority**: `CTree` currently uses `ChatGPT_API` and OpenAI chat
completions for topic generation, classification, and summaries.

**Independent Test**: The plan identifies whether tree-building changes belong
in PR001 or a follow-up PR, with explicit non-goals.

## Edge Cases

- No provider API key is configured.
- A provider/model name is unsupported.
- Streaming and non-streaming retrieval diverge in provider behavior.
- Existing users depend on the current `query_ctree` signature.
- Provider abstraction accidentally requires live network calls in tests.

## Requirements

### Functional Requirements

- **FR-001**: Retrieval MUST support explicit provider/model configuration.
- **FR-002**: Retrieval MUST preserve current Anthropic-compatible behavior by
  default unless a migration note says otherwise.
- **FR-003**: Provider selection MUST be testable with fake/no-key clients.
- **FR-004**: Unsupported provider/model configuration MUST fail before
  entering the retrieval loop.
- **FR-005**: Streaming and non-streaming retrieval MUST share the same provider
  configuration model or document any temporary limitation.
- **FR-006**: No tests may require `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or
  any real provider credential.

### Key Entities

- **LLMProviderConfig**: Provider name, model, API key/env-key resolution, and
  streaming capability.
- **RetrievalLLMClient**: Minimal interface used by `query_ctree` and
  `query_ctree_streaming`.
- **FakeRetrievalClient**: Test double for provider-selection and tool-loop
  tests.

## Success Criteria

- **SC-001**: New provider-selection tests run without network calls.
- **SC-002**: Existing baseline tests continue to pass.
- **SC-003**: `query_ctree` no longer embeds a single hardcoded model path as
  the only supported option.
- **SC-004**: The README or quickstart explains the provider/model choice.

## Assumptions

- Anthropic remains the default retrieval provider for backward compatibility.
- OpenAI tree-building provider work can be staged separately if PR001 would
  otherwise grow too large.
- Speculoos PR001 should prioritize a small, reviewable implementation over a
  full provider framework.
