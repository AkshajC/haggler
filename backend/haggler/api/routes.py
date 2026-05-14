"""API routes.

Two endpoints to start:
  POST /api/searches      — kick off a new search
  GET  /api/searches/{id} — poll for current state (frontend uses this)
"""

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from haggler.models.schemas import SearchCriteria, SearchJob

router = APIRouter()

# TODO: replace with real DB-backed storage
_JOBS: dict[str, SearchJob] = {}


@router.post("/searches", status_code=201)
async def create_search(criteria: SearchCriteria) -> dict[str, str]:
    """Start a new search job. Returns the job ID for polling."""
    from datetime import UTC, datetime

    job_id = str(uuid4())
    now = datetime.now(UTC)
    job = SearchJob(
        id=job_id,
        criteria=criteria,
        created_at=now,
        updated_at=now,
    )
    _JOBS[job_id] = job
    # TODO: kick off orchestrator as a background task
    return {"id": job_id, "status": "running"}


@router.get("/searches/{job_id}")
async def get_search(job_id: str) -> SearchJob:
    """Get current state of a search job."""
    job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
