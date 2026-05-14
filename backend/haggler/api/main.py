"""FastAPI application entrypoint."""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from haggler.api.routes import router
from haggler.config import get_settings

settings = get_settings()
log = structlog.get_logger()

app = FastAPI(
    title="Haggler API",
    version="0.1.0",
    description="AI negotiator agent for online marketplaces",
)

# Allow the Next.js dev server to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup() -> None:
    log.info("haggler.startup", model=settings.anthropic_model)
