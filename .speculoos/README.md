# Speculoos Workflow State

This directory stores repo-local workflow state for the ChatIndex fork.

- `goal.md`: objective, scope, gates, and acceptance criteria.
- `manifest.yaml`: canonical v0 state for task surfaces, lanes, and gates.
- `tasks/`: task-level readiness and acceptance records.
- `surfaces/`: external IDs and URLs for GitHub and Vibe Kanban.
- `lane-contracts/`: executor and authority boundaries.

Useful local dry-run helpers:

```bash
scripts/speculoos-loop status --repo /path/to/ChatIndex
scripts/speculoos-loop preflight --repo /path/to/ChatIndex --task <task-id>
scripts/speculoos-loop start --repo /path/to/ChatIndex --task <task-id>
scripts/speculoos-loop validate --repo /path/to/ChatIndex --task <task-id>
scripts/speculoos-loop surface-sync --repo /path/to/ChatIndex --task <task-id>
scripts/speculoos-loop close --repo /path/to/ChatIndex --task <task-id>
scripts/speculoos-loop debrief --repo /path/to/ChatIndex --task <task-id>
```

Use `release-plan` only for release-gated work such as a `dev` to `main`
promotion, tag, or GitHub Release. It is dry-run/no-write planning evidence:

```bash
scripts/speculoos-loop release-plan --repo /path/to/ChatIndex \
  --task <task-id> --pr <task-pr> --release-pr <promotion-pr> \
  --release-tag <tag> --previous-tag <previous-or-none> \
  --version-policy SemVer --release-notes-source RELEASE_NOTES.md
```

Normal docs, metadata, and maintenance PRs do not need `release-plan`.

Review caveat:

CodeRabbit can skip automatic review for PRs that target a non-default branch
such as the fork `dev` branch. Treat CI and manual Speculoos validation as the
required gate unless CodeRabbit review is explicitly triggered or repository
settings are changed to review `dev`-targeted PRs.

Do not commit private run logs, provider keys, raw private sessions, or executor
payloads. Runtime artifacts belong in private OpenClaw storage.