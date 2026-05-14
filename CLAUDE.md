# Haggler — Project Guide for Claude Code

## What this is

An AI agent that searches marketplaces (Craigslist, eBay, Facebook Marketplace) for items a user wants to buy, negotiates with sellers in natural language, and reports back the best deal. Built for a hackathon demo, so prioritize end-to-end working flows over perfection.

## Architecture (read `docs/ARCHITECTURE.md` for details)

- `backend/haggler/scout/` — per-marketplace search modules; all return `list[Listing]`
- `backend/haggler/negotiator/` — LLM-driven negotiation agent with state machine
- `backend/haggler/messaging/` — sends/receives messages on each platform
- `backend/haggler/orchestrator/` — coordinates scout + negotiators per search job
- `backend/haggler/api/` — FastAPI endpoints
- `backend/haggler/db/` — SQLAlchemy models + session management
- `backend/haggler/models/schemas.py` — Pydantic models (single source of truth)
- `frontend/` — Next.js + Tailwind dashboard

## Key conventions

- All data flows through Pydantic models in `models/schemas.py`. Never pass raw dicts between layers.
- Use `structlog` for logging, never `print`.
- Async by default — FastAPI, httpx, asyncio. Sync only when a library forces it.
- Type hints required on all public functions. Run `mypy` before pushing significant changes.
- Tests live in `backend/tests/`, run with `uv run pytest`.
- All scouts subclass `Scout` from `scout/base.py` and implement `search(criteria) -> list[Listing]`.
- All messengers subclass `Messenger` from `messaging/base.py`.

## Adding a new marketplace

1. Add the platform to the `Platform` enum in `models/schemas.py`
2. Create `scout/<platform>.py` inheriting from `Scout`
3. Create `messaging/<platform>.py` inheriting from `Messenger`
4. Add fixture-based tests in `tests/test_scout_<platform>.py` using saved HTML/JSON responses
5. Register the new scout in `orchestrator/registry.py`

## Adding a negotiation behavior

1. Modify the system prompt in `negotiator/prompts.py`
2. If adding a new state, update `negotiator/state_machine.py` and the `NegotiationState` enum
3. Add a test case in `tests/test_negotiator.py` with a mock seller reply

## Common commands

```bash
# Backend dev server (auto-reload)
cd backend && uv run uvicorn haggler.api.main:app --reload

# Run all backend tests
cd backend && uv run pytest

# Run a specific test
cd backend && uv run pytest tests/test_scout.py::test_craigslist_parses_listing

# Lint and auto-fix
cd backend && uv run ruff check . --fix
cd backend && uv run ruff format .

# Type check
cd backend && uv run mypy haggler

# Frontend dev server
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build

# Apply database migrations
cd backend && uv run alembic upgrade head
```

## Things to avoid

- Don't put secrets in code. Use `.env` (see `.env.example` for required keys).
- Don't scrape Facebook Marketplace without the Playwright stealth setup in `scout/facebook.py`.
- Don't bypass the state machine in `negotiator/state_machine.py` — state transitions must go through `transition()`.
- Don't send real messages from tests. Use the `FakeMessenger` in `tests/fixtures/`.
- Don't commit Playwright recordings, `.db` files, or anything in `.env*`.

## Hackathon mode

- Working > clean. Refactor later.
- One marketplace end-to-end > three half-built.
- Mock external dependencies aggressively in tests — we can't depend on real eBay listings in CI.
- For the demo, pre-seed a known-good conversation with a teammate playing the seller from a second Gmail.
