"""In-memory job management for processing tracking."""

import uuid
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Job:
    """Represents a single processing job."""

    job_id: str
    status: str = "processing"  # processing, completed, failed
    progress: int = 0  # 0-100
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    input_file: Optional[Path] = None
    output_file: Optional[Path] = None
    owner: Optional[str] = None  # Hashed API key for ownership


class JobManager:
    """Manages in-memory job tracking."""

    def __init__(self):
        """Initialize job manager."""
        self.jobs: Dict[str, Job] = {}

    def create_job(self) -> str:
        """Create a new job and return its ID.

        Returns:
            str: Unique job ID (UUID)
        """
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = Job(job_id=job_id)
        logger.info(f"Created job {job_id}")
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job object if exists, None otherwise
        """
        return self.jobs.get(job_id)

    def update_progress(self, job_id: str, progress: int) -> None:
        """Update job progress.

        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
        """
        job = self.get_job(job_id)
        if job:
            job.progress = min(100, max(0, progress))
            logger.debug(f"Job {job_id} progress: {job.progress}%")

    def mark_completed(self, job_id: str, output_file: Optional[Path] = None) -> None:
        """Mark job as completed.

        Args:
            job_id: Job identifier
            output_file: Path to output ZIP file
        """
        job = self.get_job(job_id)
        if job:
            job.status = "completed"
            job.progress = 100
            job.completed_at = datetime.now()
            job.output_file = output_file
            logger.info(f"Job {job_id} completed")

    def mark_failed(self, job_id: str, error: str) -> None:
        """Mark job as failed.

        Args:
            job_id: Job identifier
            error: Error message
        """
        job = self.get_job(job_id)
        if job:
            job.status = "failed"
            job.error = error
            job.completed_at = datetime.now()
            logger.error(f"Job {job_id} failed: {error}")

    def set_input_file(self, job_id: str, file_path: Path) -> None:
        """Set input file path for job.

        Args:
            job_id: Job identifier
            file_path: Path to input file
        """
        job = self.get_job(job_id)
        if job:
            job.input_file = file_path

    def set_owner(self, job_id: str, owner: str) -> None:
        """Set job owner (hashed API key).

        Args:
            job_id: Job identifier
            owner: Hashed API key
        """
        job = self.get_job(job_id)
        if job:
            job.owner = owner
            logger.debug(f"Job {job_id} owner set to {owner}")

    def verify_ownership(self, job_id: str, owner: str) -> bool:
        """Verify job ownership.

        Args:
            job_id: Job identifier
            owner: Hashed API key to check

        Returns:
            True if owner matches, False otherwise
        """
        job = self.get_job(job_id)
        if not job:
            return False
        return job.owner == owner

    def cleanup_job(self, job_id: str) -> None:
        """Clean up job files and remove from memory.

        Args:
            job_id: Job identifier
        """
        job = self.get_job(job_id)
        if job:
            # Delete temporary files
            if job.input_file and job.input_file.exists():
                try:
                    job.input_file.unlink()
                    logger.debug(f"Deleted input file: {job.input_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete input file: {e}")

            # Keep output file for download, but mark for cleanup after retention period
            logger.info(f"Job {job_id} cleaned up")


# Global job manager instance
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get or create global job manager instance.

    Returns:
        JobManager: Global job manager
    """
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
