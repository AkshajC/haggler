# Decisions

A running log of architectural decisions, kept short. When in doubt, add a new entry — future you will thank you.

## 2026-05-13: Initial stack

- **Backend language**: Python 3.11+. Best ecosystem for LLMs, scraping, and async I/O.
- **Backend framework**: FastAPI. Async-first, Pydantic-native, great docs.
- **Package manager**: uv. ~10× faster than pip, replaces poetry.
- **Frontend**: Next.js + TypeScript + Tailwind. Standard, fast to bootstrap.
- **State updates**: Polling every 2s. WebSockets are overkill for a 2-day build.
- **Database**: SQLite for hackathon. Migrate to Postgres if/when needed.
- **LLM**: Claude Sonnet 4.6 via Anthropic API. Best at natural casual tone.

## 2026-05-13: First marketplace = Craigslist

- Email relay = async by nature, perfect for the parallel-negotiation demo
- No anti-bot fight (vs. Facebook)
- No SDK setup overhead (vs. eBay)
- Risk: replies are slow. Mitigation: pre-seed a conversation with a teammate playing seller.

## 2026-05-13: Demo item = couches

- Listings are plentiful, prices have negotiation room, photos are easy to show.
- Hardcoding the category lets us tune ranking and the negotiation prompt for one domain.

## 2026-05-13: Two-person build split

- Person 1: Scout + Messaging
- Person 2: Negotiator + Orchestrator + Frontend
- Sync via `models/schemas.py` — agree on data shapes, then work independently.

## Template for new entries

```
## YYYY-MM-DD: Short title

- Context
- Decision
- Trade-offs / alternatives considered
```
