import os
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .jobicy import fetch_jobs as fetch_jobicy_jobs
from .remotive import fetch_jobs as fetch_remotive_jobs
from ..models import Job, IngestionLog


def parse_date(value):
    """
    Convert a source date into a Python datetime.
    """

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except (ValueError, TypeError):
        return None


def normalize_jobicy_job(job: dict) -> dict:
    """
    Convert a Jobicy job into JobFlow's standard format.
    """

    return {
        "external_id": str(job.get("id")),
        "source": "jobicy",
        "title": job.get("jobTitle", "Unknown"),
        "company": job.get("companyName", "Unknown"),
        "location": job.get("jobGeo"),
        "job_type": ", ".join(job.get("jobType", [])),
        "url": job.get("url"),
        "posted_at": parse_date(job.get("pubDate")),
    }


def normalize_remotive_job(job: dict) -> dict:
    """
    Convert a Remotive job into JobFlow's standard format.
    """

    return {
        "external_id": str(job.get("id")),
        "source": "remotive",
        "title": job.get("title", "Unknown"),
        "company": job.get("company_name", "Unknown"),
        "location": job.get("candidate_required_location"),
        "job_type": job.get("job_type"),
        "url": job.get("url"),
        "posted_at": parse_date(job.get("publication_date")),
    }


def validate_job(job: dict) -> bool:
    """
    Check that required fields exist.
    """

    return bool(
        job.get("external_id")
        and job.get("title")
        and job.get("company")
        and job.get("url")
    )


async def ingest_jobs(count: int = 5) -> dict:
    """
    Try Jobicy first.
    If Jobicy fails, use Remotive as fallback.
    """

    try:
        if os.getenv("SIMULATE_PRIMARY_FAILURE") == "true":
            raise RuntimeError(
                "Simulated Jobicy failure for fallback testing"
            )
        
        if os.getenv("SIMULATE_EMPTY_PRIMARY") == "true":
            raw_jobs = []
        else:
            raw_jobs = await fetch_jobicy_jobs(count)

        normalized_jobs = [
            normalize_jobicy_job(job)
            for job in raw_jobs
        ]

        normalized_jobs = [
            job
            for job in normalized_jobs
            if validate_job(job)
        ]

        if normalized_jobs:
            return {
                "source": "jobicy",
                "fallback_used": False,
                "jobs": normalized_jobs
            }

        raise RuntimeError("Jobicy returned no valid jobs")

    except Exception as error:
        print(f"Primary source failed: {error}")
        print("Switching to Remotive fallback...")

        raw_jobs = await fetch_remotive_jobs(count)

        normalized_jobs = [
            normalize_remotive_job(job)
            for job in raw_jobs
        ]

        normalized_jobs = [
            job
            for job in normalized_jobs
            if validate_job(job)
        ]

        return {
            "source": "remotive",
            "fallback_used": True,
            "jobs": normalized_jobs
        }


def save_jobs(db: Session, jobs: list[dict], source: str, fallback_used: bool) -> dict:
    """
    Save normalized jobs into SQLite and record the ingestion run.
    """

    inserted = 0
    skipped = 0

    for job_data in jobs:

        existing_job = (
            db.query(Job)
            .filter(
                Job.source == job_data["source"],
                Job.external_id == job_data["external_id"]
            )
            .first()
        )

        if existing_job:
            skipped += 1
            continue

        job = Job(**job_data)

        db.add(job)

        try:
            db.commit()
            inserted += 1

        except IntegrityError:
            db.rollback()
            skipped += 1

    log = IngestionLog(
        source=source,
        fallback_used=str(fallback_used),
        jobs_fetched=len(jobs),
        jobs_inserted=inserted,
        jobs_skipped=skipped,
        status="success"
    )

    db.add(log)
    db.commit()

    return {
        "inserted": inserted,
        "skipped": skipped,
        "total": len(jobs)
    }