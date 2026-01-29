"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import csv
import os

from moodlelogsmart.main import app

# Set test API key for tests
TEST_API_KEY = "test-api-key-12345"
os.environ["API_KEYS"] = TEST_API_KEY
os.environ["ENVIRONMENT"] = "development"


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_csv():
    """Create a sample CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        writer = csv.DictWriter(
            f, fieldnames=["Time", "Event name", "Component", "User full name"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "Time": "2024-01-15 10:30:45",
                "Event name": "Course module viewed",
                "Component": "File",
                "User full name": "John Doe",
            }
        )
        writer.writerow(
            {
                "Time": "2024-01-15 10:31:00",
                "Event name": "Submission created",
                "Component": "Assignment",
                "User full name": "John Doe",
            }
        )
        return f.name


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_csv_success(client, sample_csv):
    """Test successful CSV upload with valid API key."""
    with open(sample_csv, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": f},
            headers={"X-API-Key": TEST_API_KEY}
        )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"


def test_upload_no_api_key(client, sample_csv):
    """Test upload without API key returns 401."""
    with open(sample_csv, "rb") as f:
        response = client.post("/api/upload", files={"file": f})

    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]


def test_upload_invalid_api_key(client, sample_csv):
    """Test upload with invalid API key returns 401."""
    with open(sample_csv, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": f},
            headers={"X-API-Key": "invalid-key"}
        )

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_upload_invalid_file(client):
    """Test upload with invalid file type."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f:
        f.write("not a csv")
        f.flush()

        with open(f.name, "rb") as file:
            response = client.post(
                "/api/upload",
                files={"file": file},
                headers={"X-API-Key": TEST_API_KEY}
            )

    assert response.status_code == 400
    assert "Only .csv files are allowed" in response.json()["detail"]


def test_status_not_found(client):
    """Test status endpoint with non-existent job."""
    response = client.get("/api/status/invalid-job-id")
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]


def test_status_processing(client, sample_csv):
    """Test status endpoint for processing job."""
    # Upload file
    with open(sample_csv, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": f},
            headers={"X-API-Key": TEST_API_KEY}
        )

    job_id = upload_response.json()["job_id"]

    # Check status
    response = client.get(
        f"/api/status/{job_id}",
        headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] in ["processing", "completed", "failed"]
    assert 0 <= data["progress"] <= 100


def test_status_other_user_job(client, sample_csv):
    """Test accessing another user's job returns 403."""
    # User 1 creates job
    with open(sample_csv, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": f},
            headers={"X-API-Key": TEST_API_KEY}
        )

    job_id = upload_response.json()["job_id"]

    # User 2 tries to access (different API key)
    os.environ["API_KEYS"] = f"{TEST_API_KEY},another-test-key"
    response = client.get(
        f"/api/status/{job_id}",
        headers={"X-API-Key": "another-test-key"}
    )

    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_download_not_found(client):
    """Test download with non-existent job."""
    response = client.get("/api/download/invalid-job-id")
    assert response.status_code == 404


def test_download_not_completed(client, sample_csv):
    """Test download endpoint for job not yet completed."""
    # Upload file
    with open(sample_csv, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": f},
            headers={"X-API-Key": TEST_API_KEY}
        )

    job_id = upload_response.json()["job_id"]

    # Try to download immediately (likely still processing)
    response = client.get(
        f"/api/download/{job_id}",
        headers={"X-API-Key": TEST_API_KEY}
    )
    # Either 404 (file not found) or 400 (not completed)
    assert response.status_code in [400, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
