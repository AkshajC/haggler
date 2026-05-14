# Backend

Python + FastAPI. See [`docs/SETUP.md`](../docs/SETUP.md) for first-time setup.

## Layout

```
haggler/
├── api/          # FastAPI routes and app entrypoint
├── orchestrator/ # Coordinates scout + negotiator per search
├── scout/        # Per-marketplace search modules
├── negotiator/   # LLM negotiation logic + state machine
├── messaging/    # Platform messaging adapters
├── models/       # Pydantic schemas (shared contracts)
├── db/           # SQLAlchemy models and session
└── config.py     # Settings via pydantic-settings
```

## Common commands

```bash
# Dev server
uv run uvicorn haggler.api.main:app --reload

# Tests
uv run pytest
uv run pytest tests/test_schemas.py -v

# Lint + format
uv run ruff check . --fix
uv run ruff format .

# Type check
uv run mypy haggler

# Add a dependency
uv add httpx
uv add --dev pytest-mock  # dev-only

# Run a one-off script
uv run python -c "from haggler.config import get_settings; print(get_settings())"
```

## Adding a new scout

1. Add to the `Platform` enum in `models/schemas.py`
2. Create `scout/<name>.py` inheriting from `Scout`
3. Implement `async def search(self, criteria) -> list[Listing]`
4. Add tests in `tests/test_scout_<name>.py`. Use saved HTML/JSON fixtures, don't hit the live site in CI.

## Adding a new messenger

Same pattern — subclass `Messenger`, implement `send` and `poll_replies`.
