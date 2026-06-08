# Quickstart: Multi-LLM Support

## No-Key Validation

```bash
python -m unittest discover -v
```

The PR001 tests must use fake clients and must not require real provider API
keys.

## Expected User Shape

Existing calls should continue to work:

```python
result = query_ctree(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    ctree=tree,
    user_query="What was discussed?"
)
```

New calls should be able to select provider/model explicitly:

```python
result = query_ctree(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    ctree=tree,
    user_query="What was discussed?",
    provider="anthropic",
    model="claude-sonnet-4-5"
)
```

The final API may use a config object if the implementation proves that cleaner.
