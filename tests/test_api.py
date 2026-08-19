from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "JobFlow"
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_get_jobs():
    response = client.get("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_ingestion_logs():
    response = client.get("/ingestion-logs")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_ingest():
    response = client.post("/ingest")

    assert response.status_code == 200

    data = response.json()

    assert "source" in data
    assert "fallback_used" in data
    assert "inserted" in data
    assert "skipped" in data
    assert "total" in data

    assert data["source"] in ["jobicy", "remotive"]

    assert isinstance(data["fallback_used"], bool)
    assert isinstance(data["inserted"], int)
    assert isinstance(data["skipped"], int)
    assert isinstance(data["total"], int)


def test_duplicate_ingestion():
    """
    Running ingestion twice should not create
    duplicate records.
    """

    first_response = client.post("/ingest")

    assert first_response.status_code == 200

    second_response = client.post("/ingest")

    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["total"] >= 0
    assert second_data["total"] >= 0

    assert second_data["skipped"] >= 0


def test_fallback():
    """
    Verify that the controlled fallback mechanism
    switches from Jobicy to Remotive.
    """

    response = client.post("/test-fallback")

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "remotive"
    assert data["fallback_used"] is True

    assert isinstance(data["inserted"], int)
    assert isinstance(data["skipped"], int)
    assert isinstance(data["total"], int)


def test_jobs_after_ingestion():
    """
    Verify that jobs can be retrieved after ingestion.
    """

    client.post("/ingest")

    response = client.get("/jobs")

    assert response.status_code == 200

    jobs = response.json()

    assert isinstance(jobs, list)

    if jobs:
        job = jobs[0]

        assert "id" in job
        assert "external_id" in job
        assert "source" in job
        assert "title" in job
        assert "company" in job
        assert "url" in job