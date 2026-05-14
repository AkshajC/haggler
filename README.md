# Haggler

An AI negotiator agent that searches online marketplaces for items you want to buy, messages sellers, and negotiates in natural language to get you the best deal.

## What it does

1. You tell it what you want: "black mid-sized couch under $400 near San Ramon"
2. It scouts Craigslist, eBay, and Facebook Marketplace for matching listings
3. It opens parallel negotiations with multiple sellers via each platform's messaging
4. It reports back the best deal with a link and full conversation transcript

## Project structure

```
haggler/
├── backend/          # Python: FastAPI, scout, negotiator, orchestrator
├── frontend/         # Next.js dashboard with live status updates
├── docs/             # Architecture, decisions, demo script
├── .github/          # CI workflows
└── CLAUDE.md         # Guide for Claude Code
```

See `docs/ARCHITECTURE.md` for the system design and `docs/DECISIONS.md` for choices made.

## Quickstart

### Prerequisites
- Python 3.11+
- Node 20+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Setup

```bash
# Clone and enter
git clone git@github.com:<your-org>/haggler.git
cd haggler

# Backend
cd backend
uv sync
uv run playwright install chromium
cp .env.example .env  # then fill in API keys

# Frontend (in a new terminal)
cd frontend
npm install
cp .env.example .env.local

# Pre-commit hooks (from repo root)
cd ..
uv tool install pre-commit
pre-commit install
```

### Running locally

```bash
# Backend
cd backend && uv run uvicorn haggler.api.main:app --reload

# Frontend
cd frontend && npm run dev
```

Backend runs on http://localhost:8000, frontend on http://localhost:3000.

## Development workflow

- Work on feature branches: `feat/<short-name>`
- Open a PR to `main`, get one review, squash-merge
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- Tests required for any new scout or messenger module
- Run `uv run pytest` and `uv run ruff check .` before pushing

## Team

- Person 1 — Scout + Messaging layer
- Person 2 — Negotiator + Orchestrator + Frontend
