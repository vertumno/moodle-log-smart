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


# ============================================================================
# Story 2.6: Timeout and Cleanup Tests
# ============================================================================


@pytest.mark.asyncio
async def test_job_timeout():
    """Test job timeout detection (Story 2.6)."""
    import asyncio
    from unittest.mock import patch
    from moodlelogsmart.main import process_job_with_timeout
    from moodlelogsmart.api.job_manager import get_job_manager

    job_manager = get_job_manager()

    # Create a job
    job_id = job_manager.create_job()

    # Mock process_job to take longer than timeout
    async def slow_job(job_id, input_file):
        await asyncio.sleep(5)  # 5 seconds

    # Set very short timeout for testing (1 second)
    with patch("moodlelogsmart.main.JOB_TIMEOUT_SECONDS", 1):
        with patch("moodlelogsmart.main.process_job", slow_job):
            await process_job_with_timeout(job_id, "test.csv")

    # Verify job marked as failed with timeout
    job = job_manager.get_job(job_id)
    assert job is not None
    assert job.status == "failed"
    assert "timeout" in job.error.lower()


def test_cleanup_job_manager():
    """Test JobManager cleanup_job method (Story 2.6)."""
    import tempfile
    from moodlelogsmart.api.job_manager import get_job_manager
    from pathlib import Path

    job_manager = get_job_manager()

    # Create a job with temporary files
    job_id = job_manager.create_job()

    # Create fake input and output files
    temp_dir = Path(tempfile.gettempdir()) / "moodlelogsmart"
    temp_dir.mkdir(parents=True, exist_ok=True)

    input_file = temp_dir / f"{job_id}_input.csv"
    output_file = temp_dir / f"{job_id}_output.zip"

    input_file.write_text("test,data\n1,2")
    output_file.write_text("fake zip content")

    # Set files in job
    job_manager.set_input_file(job_id, input_file)
    job_manager.mark_completed(job_id, output_file)

    # Verify files exist
    assert input_file.exists()
    assert output_file.exists()

    # Cleanup job
    job_manager.cleanup_job(job_id)

    # Verify files deleted
    assert not input_file.exists()
    assert not output_file.exists()


@pytest.mark.asyncio
async def test_cleanup_old_jobs():
    """Test cleanup_old_jobs TTL logic (Story 2.6)."""
    from datetime import datetime, timedelta
    from unittest.mock import patch
    from moodlelogsmart.api.job_manager import get_job_manager
    from moodlelogsmart.main import cleanup_old_jobs
    import asyncio

    job_manager = get_job_manager()

    # Create completed job 25 hours ago (should be cleaned)
    old_job_id = job_manager.create_job()
    job_manager.mark_completed(old_job_id, None)
    old_job = job_manager.get_job(old_job_id)
    old_job.completed_at = datetime.now() - timedelta(hours=25)

    # Create recent job 1 hour ago (should NOT be cleaned)
    recent_job_id = job_manager.create_job()
    job_manager.mark_completed(recent_job_id, None)

    # Create failed job 2 hours ago (should be cleaned, TTL=1h for failed)
    failed_job_id = job_manager.create_job()
    job_manager.mark_failed(failed_job_id, "Test error")
    failed_job = job_manager.get_job(failed_job_id)
    failed_job.completed_at = datetime.now() - timedelta(hours=2)

    # Set short cleanup interval for testing
    with patch("moodlelogsmart.main.CLEANUP_INTERVAL_SECONDS", 0.1):
        # Start cleanup task
        cleanup_task = asyncio.create_task(cleanup_old_jobs())

        # Wait for one cleanup cycle
        await asyncio.sleep(0.2)

        # Cancel cleanup task
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

    # Verify old job cleaned
    assert job_manager.get_job(old_job_id) is None

    # Verify recent job still exists
    assert job_manager.get_job(recent_job_id) is not None

    # Verify old failed job cleaned
    assert job_manager.get_job(failed_job_id) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
