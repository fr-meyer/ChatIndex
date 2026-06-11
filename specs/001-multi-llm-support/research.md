# Research: Multi-LLM Support

## Current Findings

- The README roadmap lists **Multi-LLM support** as an open item.
- Retrieval is currently Anthropic-specific:
  - `retrieval/llm_tools.py` imports `Anthropic`.
  - `query_ctree` and `query_ctree_streaming` create Anthropic clients directly.
  - Both paths hardcode `claude-sonnet-4-5`.
- Tree-building is currently OpenAI-specific:
  - `ctree/utils.py` defines `ChatGPT_API`.
  - `CTree` uses `OPENAI_API_KEY` and `ChatGPT_API` for summaries, topic
    classification, and splitting.

## Decision

Start with retrieval provider abstraction because it is the explicit roadmap
wording and has a smaller surface than tree-building.

## Alternatives Considered

- **Full provider abstraction for tree-building and retrieval in one PR**:
  rejected for PR001 because it would touch many LLM call sites and weaken the
  first dogfood signal.
- **Only make the hardcoded model configurable**: rejected as too narrow because
  provider selection would still be baked into `Anthropic`.
- **Adopt LiteLLM immediately**: deferred. It may be useful later, but PR001
  should first make ChatIndex's own provider seam clear and testable.
