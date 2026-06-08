# ChatIndex Constitution

## Core Principles

### I. Lossless Conversation Provenance

ChatIndex changes must preserve access to original conversation messages. Topic
summaries, routing metadata, vector indexes, and other derived structures may
accelerate retrieval, but they must not replace or obscure raw message leaves.

### II. Provider-Portability by Default

Core tree-building, retrieval, and evaluation paths should work with fake or
local test providers by default. Real OpenAI, Anthropic, or other provider keys
are optional validation inputs and must not be required for unit tests.

### III. Testable Before External Calls

Every roadmap PR must add or update tests that run without secrets and without
network calls. External-provider smoke tests may be documented separately and
must be opt-in.

### IV. Small PRs With Reviewable Artifacts

Each roadmap item maps to one focused branch and one pull request. Spec, plan,
tasks, test evidence, and review notes must make the change understandable
without relying on an agent transcript.

### V. Private Data Stays Out

Repository fixtures must be synthetic, public, or explicitly sanitized. Do not
commit private OpenClaw sessions, API keys, provider responses that contain
private inputs, raw executor logs, or generated run payloads.

## Development Workflow

- Use Spec Kit artifacts under `specs/` for roadmap work.
- Use `.speculoos/` to record task readiness, surface mappings, lane contracts,
  and review gates.
- Keep implementation branches based on the fork `dev` branch when the fork is
  available.
- Run local tests before proposing a PR.
- Record any provider-key smoke test as optional evidence, never as the only
  acceptance path.

## Governance

This constitution guides ChatIndex fork work until superseded by a reviewed
change. Amendments require a focused PR that explains the reason, migration
impact, and affected specs/tasks.

**Version**: 0.1.0 | **Ratified**: 2026-06-05 | **Last Amended**: 2026-06-05
