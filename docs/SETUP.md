# Setup guide

Step-by-step from empty machine to running Haggler locally. Should take ~30 minutes the first time.

## 1. Install prerequisites

### Python 3.11+

Check: `python3 --version`. If you need it, use [pyenv](https://github.com/pyenv/pyenv) or your OS package manager.

### Node 20+

Check: `node --version`. Use [nvm](https://github.com/nvm-sh/nvm) if you need to install.

### uv (Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your shell or `source ~/.bashrc`.

### Claude Code (optional but recommended)

```bash
npm install -g @anthropic-ai/claude-code
```

Run `claude` once from any directory to authenticate.

## 2. Clone and install

```bash
git clone git@github.com:<your-org>/haggler.git
cd haggler

# Backend
cd backend
uv sync
uv run playwright install chromium
cp .env.example .env
# now edit .env and add your ANTHROPIC_API_KEY

# Frontend
cd ../frontend
npm install
cp .env.example .env.local

# Pre-commit hooks (from repo root)
cd ..
uv tool install pre-commit
pre-commit install
```

## 3. Get your API keys

### Anthropic (required)

1. Sign up at https://console.anthropic.com
2. Settings → API Keys → Create Key
3. Paste into `backend/.env` as `ANTHROPIC_API_KEY`

### eBay (optional for hackathon)

1. Sign up at https://developer.ebay.com
2. Create an app, get App ID and Cert ID
3. Use the sandbox keys first (`EBAY_SANDBOX=true`)

### Gmail (for Craigslist email relay)

1. Create a throwaway Gmail account
2. Enable 2-factor auth
3. Generate an app password: https://myaccount.google.com/apppasswords
4. Add to `.env` as `GMAIL_USER` and `GMAIL_APP_PASSWORD`

## 4. Verify everything works

```bash
# Backend tests
cd backend
uv run pytest

# Backend dev server
uv run uvicorn haggler.api.main:app --reload
# Visit http://localhost:8000/health — should return {"status": "ok"}
# Visit http://localhost:8000/docs — interactive API docs

# Frontend (in a new terminal)
cd frontend
npm run dev
# Visit http://localhost:3000
```

## 5. VS Code setup

Recommended extensions:

- Python (Microsoft)
- Ruff (Astral)
- Pylance (Microsoft)
- ES7+ React snippets
- Tailwind CSS IntelliSense
- GitLens

Workspace settings (create `.vscode/settings.json`):

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "python.defaultInterpreterPath": "backend/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["backend/tests"]
}
```

## Common issues

**`uv sync` fails on Playwright**: Run `uv run playwright install --with-deps chromium` to also pull system deps.

**Pre-commit blocks a commit**: It auto-fixes most things. Run `git add -u` and re-commit.

**Frontend can't reach backend**: Make sure `NEXT_PUBLIC_API_URL` in `frontend/.env.local` matches your backend port.
