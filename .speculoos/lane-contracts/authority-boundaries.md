# Authority Boundaries

OpenClaw owns durable orchestration, memory, policy, final review, and publish
approval. Executor lanes may propose changes but do not own acceptance.

## Default Deny

Executors may not:

- read or write secrets;
- commit, push, open PRs, merge, or release;
- send external messages;
- change workflow authority boundaries;
- write private OpenClaw logs into this repository.

## Publish Gate

Commit, push, and PR creation require explicit approval after:

- diff review;
- test evidence;
- private-data check;
- surface sync check;
- acceptance decision.
