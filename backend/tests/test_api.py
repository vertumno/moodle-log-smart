"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import csv

from moodlelogsmart.main import app


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
    """Test successful CSV upload."""
    with open(sample_csv, "rb") as f:
        response = client.post("/api/upload", files={"file": f})

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"


def test_upload_invalid_file(client):
    """Test upload with invalid file type."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f:
        f.write("not a csv")
        f.flush()

        with open(f.name, "rb") as file:
            response = client.post("/api/upload", files={"file": file})

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
        upload_response = client.post("/api/upload", files={"file": f})

    job_id = upload_response.json()["job_id"]

    # Check status
    response = client.get(f"/api/status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] in ["processing", "completed", "failed"]
    assert 0 <= data["progress"] <= 100


def test_download_not_found(client):
    """Test download with non-existent job."""
    response = client.get("/api/download/invalid-job-id")
    assert response.status_code == 404


def test_download_not_completed(client, sample_csv):
    """Test download endpoint for job not yet completed."""
    # Upload file
    with open(sample_csv, "rb") as f:
        upload_response = client.post("/api/upload", files={"file": f})

    job_id = upload_response.json()["job_id"]

    # Try to download immediately (likely still processing)
    response = client.get(f"/api/download/{job_id}")
    # Either 404 (file not found) or 400 (not completed)
    assert response.status_code in [400, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
