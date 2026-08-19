from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Job, IngestionLog
from .services.ingestion import ingest_jobs, save_jobs


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="JobFlow API",
    description="Resilient job ingestion pipeline",
    version="1.0.0",
)


# Enable CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "JobFlow",
        "status": "running",
        "message": "Job ingestion API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ingest")
async def ingest(
    db: Session = Depends(get_db)
):
    ingestion_result = await ingest_jobs(5)

    result = save_jobs(
        db,
        ingestion_result["jobs"],
        ingestion_result["source"],
        ingestion_result["fallback_used"]
    )

    return {
        "source": ingestion_result["source"],
        "fallback_used": ingestion_result["fallback_used"],
        **result
    }


@app.post("/test-fallback")
async def test_fallback(
    db: Session = Depends(get_db)
):
    """
    Controlled local test of the fallback mechanism.

    This temporarily simulates a primary Jobicy
    failure and verifies that Remotive is used.
    """

    import os

    previous_value = os.environ.get(
        "SIMULATE_PRIMARY_FAILURE"
    )

    os.environ["SIMULATE_PRIMARY_FAILURE"] = "true"

    try:

        ingestion_result = await ingest_jobs(5)

        result = save_jobs(
            db,
            ingestion_result["jobs"],
            ingestion_result["source"],
            ingestion_result["fallback_used"]
        )

        return {
            "source": ingestion_result["source"],
            "fallback_used": ingestion_result["fallback_used"],
            **result
        }

    finally:

        if previous_value is None:

            os.environ.pop(
                "SIMULATE_PRIMARY_FAILURE",
                None
            )

        else:

            os.environ[
                "SIMULATE_PRIMARY_FAILURE"
            ] = previous_value


@app.get("/jobs")
def get_jobs(
    db: Session = Depends(get_db)
):
    jobs = (
        db.query(Job)
        .all()
    )

    return jobs


@app.get("/ingestion-logs")
def get_ingestion_logs(
    db: Session = Depends(get_db)
):
    logs = (
        db.query(IngestionLog)
        .order_by(
            IngestionLog.id.desc()
        )
        .all()
    )

    return logs