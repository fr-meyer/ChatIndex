# Quickstart: Fork Dev Baseline

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Baseline Validation

```bash
python -m unittest discover -v
```

Expected PR 0 behavior:

- Tests must not require `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
- No `.env` file is required.
- Private run logs are not committed.

## Speculoos State

Inspect these files before executor work:

```bash
sed -n '1,220p' .speculoos/goal.md
sed -n '1,220p' .speculoos/manifest.yaml
sed -n '1,220p' .speculoos/tasks/pr-000-fork-dev-baseline.yaml
```
