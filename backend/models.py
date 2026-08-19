from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    external_id = Column(
        String,
        nullable=False,
        index=True
    )

    source = Column(
        String,
        nullable=False,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    company = Column(
        String,
        nullable=False
    )

    location = Column(String)

    job_type = Column(String)

    url = Column(
        String,
        nullable=False
    )

    posted_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_job_source_external_id"
        ),
    )


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    source = Column(
        String,
        nullable=False
    )

    fallback_used = Column(
        String,
        nullable=False
    )

    jobs_fetched = Column(
        Integer,
        default=0
    )

    jobs_inserted = Column(
        Integer,
        default=0
    )

    jobs_skipped = Column(
        Integer,
        default=0
    )

    status = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )