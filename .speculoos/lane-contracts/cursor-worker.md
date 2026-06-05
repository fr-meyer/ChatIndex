# Cursor Worker Lane Contract

## Role

Cursor is a bounded one-shot implementation lane launched by OpenClaw through
the accepted worker job contract.

## Required Inputs

- Bounded prompt.
- Explicit write scope.
- Acceptance criteria.
- Credential policy.
- Repo path and branch/worktree.

## Required Outputs

- Worker log.
- Result JSON.
- Metadata.
- Changed-file summary.
- Test output when requested.

## Limits

Default policy is no Git/SSH credentials, no commit, no push, no PR, no daemon,
and no merge. Cursor output must pass OpenClaw review before acceptance.
