# Architecture

## Overview

Haggler is a Python backend that performs two concurrent jobs for each user search: scouting marketplaces for listings, and negotiating with sellers via their platform's messaging system. A Next.js frontend polls the backend for live status updates.

## Layers

### 1. Frontend (`frontend/`)

Next.js app with a single dashboard page. Submits a search, then polls `GET /api/searches/{id}` every 2 seconds and renders listing cards with current negotiation status.

### 2. API (`backend/haggler/api/`)

FastAPI app exposing:

- `POST /api/searches` — accepts `SearchCriteria`, returns a job ID, kicks off the orchestrator
- `GET /api/searches/{id}` — returns the current `SearchJob` state

### 3. Orchestrator (`backend/haggler/orchestrator/`)

Owns the lifecycle of a single search:

1. Receives `SearchCriteria`
2. Calls every registered `Scout` in parallel; collects all `Listing`s
3. Ranks them, picks the top N
4. Spawns a `Negotiator` task for each top listing
5. Watches for state changes; updates the DB
6. Stops when "good enough" threshold is met or timeout

### 4. Scout (`backend/haggler/scout/`)

Each platform module subclasses `Scout` and exposes `search(criteria) -> list[Listing]`. The orchestrator doesn't know or care how each one works internally — Craigslist uses RSS, eBay uses their API, Facebook uses Playwright.

### 5. Negotiator (`backend/haggler/negotiator/`)

One instance per conversation. Each instance:

1. Tracks state via the `NegotiationState` enum
2. At each turn, calls the LLM with the message history + system prompt
3. LLM returns a `NegotiatorDecision` (structured output)
4. Either sends a message via the `Messenger` or waits/walks away

State transitions live in `state_machine.py` and are the only legal way to change state.

### 6. Messaging (`backend/haggler/messaging/`)

Mirrors the scout layer: one module per platform, all conforming to the `Messenger` interface (`send`, `poll_replies`). Hides whether we're talking SMTP, REST API, or Playwright.

### 7. State store (`backend/haggler/db/`)

SQLAlchemy + SQLite for the hackathon (swap to Postgres later). Three core tables: `searches`, `listings`, `conversations`, plus a `messages` table for the full transcript.

## Data flow

```
User
 │
 ▼
Frontend ── POST /api/searches ──▶ API ──▶ Orchestrator
                                              │
                          ┌───────────────────┼───────────────────┐
                          ▼                   ▼                   ▼
                    Craigslist Scout    eBay Scout         Facebook Scout
                          │                   │                   │
                          └───────────────────┼───────────────────┘
                                              ▼
                                       Rank & select top N
                                              │
                            ┌─────────────────┼─────────────────┐
                            ▼                 ▼                 ▼
                       Negotiator₁      Negotiator₂        Negotiator₃
                            │                 │                 │
                            ▼                 ▼                 ▼
                       Messenger         Messenger          Messenger
                            │                 │                 │
                            ▼                 ▼                 ▼
                       real seller       real seller        real seller
                            │                 │                 │
                            └─────────────────┼─────────────────┘
                                              ▼
                                         State store
                                              │
                                              ▼
                              Frontend polls /api/searches/{id}
```

## Why these choices

**Two abstract base classes (Scout, Messenger).** They turn "add a new marketplace" from a refactor into a drop-in. Critical because we're racing the clock and might cut Facebook entirely if Playwright fights us.

**Pydantic everywhere.** Validation at every layer boundary means a bad scrape can't silently corrupt the negotiator's view of the world.

**asyncio over threads.** Marketplaces are I/O bound. asyncio + httpx is the lowest-friction way to run 8 parallel negotiations on one machine.

**SQLite first.** Zero ops. Migrate later if we need it.

**Structured LLM output for negotiation decisions.** Lets us log and unit-test what the model "decided" separately from what it said, which is huge for prompt debugging.

## What's out of scope for the demo

- Multi-user / auth
- Production messaging volume (eBay rate limits, FB account bans)
- Payment handling
- Persistent search jobs across restarts
