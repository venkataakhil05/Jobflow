import os
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Job, IngestionLog
from .services.ingestion import ingest_jobs, save_jobs


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="JobFlow API",
    description="Resilient job ingestion pipeline",
    version="1.0.0",
)


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

@app.get("/")
def root():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


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
    Run a controlled fallback test.

    Jobicy is deliberately forced to fail.
    The existing ingestion pipeline then
    switches to Remotive.
    """

    previous_value = os.environ.get(
        "SIMULATE_PRIMARY_FAILURE"
    )

    try:

        # Force Jobicy to fail.
        os.environ[
            "SIMULATE_PRIMARY_FAILURE"
        ] = "true"

        ingestion_result = await ingest_jobs(5)

        result = save_jobs(
            db,
            ingestion_result["jobs"],
            ingestion_result["source"],
            ingestion_result["fallback_used"]
        )

        return {
            "source": ingestion_result["source"],
            "fallback_used": ingestion_result[
                "fallback_used"
            ],
            **result
        }

    finally:

        # Restore the previous environment state.
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

    jobs = db.query(Job).all()

    return jobs


@app.get("/ingestion-logs")
def get_ingestion_logs(
    db: Session = Depends(get_db)
):

    logs = (
        db.query(IngestionLog)
        .order_by(
            IngestionLog.created_at.desc()
        )
        .all()
    )

    return logs


# ---------------------------------------------------------
# FRONTEND FILES
# ---------------------------------------------------------

@app.get("/style.css")
def serve_css():

    return Response(
        content=(
            FRONTEND_DIR / "style.css"
        ).read_text(
            encoding="utf-8"
        ),
        media_type="text/css"
    )


@app.get("/app.js")
def serve_javascript():

    return Response(
        content=(
            FRONTEND_DIR / "app.js"
        ).read_text(
            encoding="utf-8"
        ),
        media_type="application/javascript"
    )