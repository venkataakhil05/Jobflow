from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
# API Routes
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ingest")
async def ingest(db: Session = Depends(get_db)):

    ingestion_result = await ingest_jobs(5)

    result = save_jobs(
        db,
        ingestion_result["jobs"]
    )

    return {
        "source": ingestion_result["source"],
        "fallback_used": ingestion_result["fallback_used"],
        **result
    }


@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):

    jobs = db.query(Job).all()

    return jobs


@app.get("/ingestion-logs")
def get_ingestion_logs(
    db: Session = Depends(get_db)
):

    logs = (
        db.query(IngestionLog)
        .order_by(IngestionLog.created_at.desc())
        .all()
    )

    return logs


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.get("/", include_in_schema=False)
def serve_frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# Serve CSS, JavaScript and other frontend files
app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_DIR,
        html=True
    ),
    name="frontend"
)