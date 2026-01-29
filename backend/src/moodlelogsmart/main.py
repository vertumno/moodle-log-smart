"""FastAPI application for MoodleLogSmart."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional
import tempfile
import zipfile
from datetime import datetime, timedelta

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from moodlelogsmart.api.models import UploadResponse, StatusResponse, ErrorResponse
from moodlelogsmart.api.job_manager import get_job_manager, Job
from moodlelogsmart.api.auth import verify_api_key

# Try to import slowapi (optional for rate limiting)
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    logger.warning("slowapi not installed - rate limiting disabled")
    RATE_LIMITING_AVAILABLE = False
from moodlelogsmart.core.auto_detect.csv_detector import CSVDetector
from moodlelogsmart.core.auto_detect.column_mapper import ColumnMapper
from moodlelogsmart.core.auto_detect.timestamp_detector import TimestampDetector
from moodlelogsmart.core.clean.data_cleaner import DataCleaner
from moodlelogsmart.core.rules.rule_engine import RuleEngine
from moodlelogsmart.core.export.exporter import CSVExporter, XESExporter

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MoodleLogSmart API",
    description="Transform Moodle logs using Bloom's Taxonomy",
    version="0.1.0",
)

# Configure rate limiting (if available)
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled")
else:
    limiter = None

# Load allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

if "*" in ALLOWED_ORIGINS:
    logger.warning("⚠️ CORS wildcard detected! Not recommended for production")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
    max_age=3600,
)

logger.info(f"CORS configured for origins: {ALLOWED_ORIGINS}")

# Get job manager
job_manager = get_job_manager()

# Temporary directory for uploads
TEMP_DIR = Path(tempfile.gettempdir()) / "moodlelogsmart"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("MoodleLogSmart API starting up")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Start cleanup background task
    asyncio.create_task(cleanup_old_jobs())
    logger.info("Cleanup task started (runs every hour)")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    api_key_id: str = Depends(verify_api_key)
) -> UploadResponse:
    """Upload CSV file for processing.

    Args:
        file: CSV file to process (max 50MB)
        background_tasks: FastAPI background tasks

    Returns:
        UploadResponse with job_id and status

    Raises:
        HTTPException: If file validation fails
    """
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed")

    # Create job
    job_id = job_manager.create_job()
    job_manager.set_owner(job_id, api_key_id)

    try:
        # Save uploaded file temporarily
        temp_input = TEMP_DIR / f"{job_id}_input.csv"
        contents = await file.read()

        # Validate file size (50MB limit)
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > 50:
            raise HTTPException(status_code=413, detail="File size exceeds 50MB limit")

        # Write to temporary file
        with open(temp_input, "wb") as f:
            f.write(contents)

        job_manager.set_input_file(job_id, temp_input)
        logger.info(f"Job {job_id}: Received {file_size_mb:.2f}MB CSV file")

        # Start background processing with timeout
        background_tasks.add_task(
            process_job_with_timeout, job_id, str(temp_input)
        )

        return UploadResponse(job_id=job_id, status="processing")

    except HTTPException:
        job_manager.mark_failed(job_id, "File validation failed")
        raise
    except Exception as e:
        logger.error(f"Job {job_id}: Upload error: {str(e)}")
        job_manager.mark_failed(job_id, f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(
    job_id: str,
    api_key_id: str = Depends(verify_api_key)
) -> StatusResponse:
    """Get job processing status.

    Args:
        job_id: Job identifier

    Returns:
        StatusResponse with current status and progress

    Raises:
        HTTPException: If job not found
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify ownership
    if not job_manager.verify_ownership(job_id, api_key_id):
        raise HTTPException(status_code=403, detail="Access denied: not your job")

    return StatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@app.get("/api/download/{job_id}")
async def download_results(
    job_id: str,
    api_key_id: str = Depends(verify_api_key)
):
    """Download processed results as ZIP.

    Args:
        job_id: Job identifier

    Returns:
        ZIP file with results

    Raises:
        HTTPException: If job not found, not completed, or file not accessible
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify ownership
    if not job_manager.verify_ownership(job_id, api_key_id):
        raise HTTPException(status_code=403, detail="Access denied: not your job")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Job status is {job.status}")

    if not job.output_file or not job.output_file.exists():
        raise HTTPException(status_code=404, detail="Results file not found")

    return FileResponse(
        path=job.output_file,
        media_type="application/zip",
        filename=job.output_file.name,
    )


# Configuration for cleanup and timeout
JOB_TIMEOUT_SECONDS = int(os.getenv("JOB_TIMEOUT_SECONDS", "600"))  # 10 minutes
CLEANUP_INTERVAL_SECONDS = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "3600"))  # 1 hour
TTL_COMPLETED_HOURS = int(os.getenv("TTL_COMPLETED_HOURS", "24"))  # 24 hours
TTL_FAILED_HOURS = int(os.getenv("TTL_FAILED_HOURS", "1"))  # 1 hour


async def process_job_with_timeout(job_id: str, input_file: str) -> None:
    """Process job with timeout protection.

    Args:
        job_id: Job identifier
        input_file: Path to input CSV

    Timeout: Configurable via JOB_TIMEOUT_SECONDS (default: 600s = 10 min)
    """
    try:
        await asyncio.wait_for(
            process_job(job_id, input_file),
            timeout=float(JOB_TIMEOUT_SECONDS)
        )
    except asyncio.TimeoutError:
        logger.error(f"Job {job_id} timed out after {JOB_TIMEOUT_SECONDS}s")
        job_manager.mark_failed(
            job_id,
            f"Processing timeout ({JOB_TIMEOUT_SECONDS // 60} minutes)"
        )
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        job_manager.mark_failed(job_id, str(e))


async def cleanup_old_jobs() -> None:
    """Periodic cleanup of old jobs and files.

    Runs every hour (configurable). Cleans up:
    - Completed jobs older than TTL_COMPLETED_HOURS (default: 24h)
    - Failed jobs older than TTL_FAILED_HOURS (default: 1h)
    - Associated files (input and output)
    """
    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

            now = datetime.now()
            jobs_to_clean = []

            for job_id, job in list(job_manager.jobs.items()):
                if not job.completed_at:
                    continue  # Skip active jobs

                age = now - job.completed_at

                # Check if TTL expired
                should_clean = False
                reason = ""
                if job.status == "completed":
                    if age > timedelta(hours=TTL_COMPLETED_HOURS):
                        should_clean = True
                        reason = f"Completed job older than {TTL_COMPLETED_HOURS}h"
                elif job.status == "failed":
                    if age > timedelta(hours=TTL_FAILED_HOURS):
                        should_clean = True
                        reason = f"Failed job older than {TTL_FAILED_HOURS}h"

                if should_clean:
                    jobs_to_clean.append((job_id, reason))

            # Clean up identified jobs
            for job_id, reason in jobs_to_clean:
                logger.info(f"Cleaning up job {job_id}: {reason}")
                job_manager.cleanup_job(job_id)
                del job_manager.jobs[job_id]

            if jobs_to_clean:
                logger.info(f"Cleanup: Removed {len(jobs_to_clean)} old jobs")

        except Exception as e:
            logger.error(f"Cleanup task error: {e}", exc_info=True)


async def process_job(job_id: str, input_file: str) -> None:
    """Process CSV file in background.

    Args:
        job_id: Job identifier
        input_file: Path to input CSV file
    """
    try:
        logger.info(f"Job {job_id}: Starting processing")
        job_manager.update_progress(job_id, 10)

        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Step 1: Detect CSV format
        logger.info(f"Job {job_id}: Detecting CSV format")
        detector = CSVDetector()
        csv_format = detector.detect(input_file)
        job_manager.update_progress(job_id, 20)

        # Step 2: Load and detect columns
        logger.info(f"Job {job_id}: Mapping columns")
        import pandas as pd

        df = pd.read_csv(
            input_file,
            encoding=csv_format.encoding,
            delimiter=csv_format.delimiter,
        )

        column_mapper = ColumnMapper()
        mapped_columns = column_mapper.map(df.columns.tolist())
        job_manager.update_progress(job_id, 30)

        # Step 3: Detect timestamp format
        logger.info(f"Job {job_id}: Detecting timestamp format")
        timestamp_detector = TimestampDetector()
        timestamp_format = timestamp_detector.detect(df)
        job_manager.update_progress(job_id, 40)

        # Step 4: Clean data
        logger.info(f"Job {job_id}: Cleaning data")
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean(df, timestamp_format)
        job_manager.update_progress(job_id, 60)

        # Step 5: Apply rules (Bloom's Taxonomy)
        logger.info(f"Job {job_id}: Enriching with Bloom taxonomy")
        rule_engine = RuleEngine()
        enriched_df = rule_engine.apply_rules(cleaned_df)
        job_manager.update_progress(job_id, 75)

        # Step 6: Export results
        logger.info(f"Job {job_id}: Exporting results")
        output_dir = TEMP_DIR / f"{job_id}_output"
        output_dir.mkdir(exist_ok=True)

        # Convert to list of dicts for exporters
        events = enriched_df.to_dict("records")

        # Export CSV formats
        csv_exporter = CSVExporter()
        csv_exporter.export(events, str(output_dir / "enriched_log.csv"))

        # Export XES if available
        try:
            xes_exporter = XESExporter()
            xes_exporter.export(events, str(output_dir / "enriched_log.xes"))
        except Exception as e:
            logger.warning(f"Job {job_id}: XES export skipped: {e}")

        # Export bloom-only versions
        bloom_only = [e for e in events if e.get("bloom_level") not in [None, "N/A"]]
        if bloom_only:
            csv_exporter.export(bloom_only, str(output_dir / "enriched_log_bloom_only.csv"))
            try:
                xes_exporter = XESExporter()
                xes_exporter.export(
                    bloom_only, str(output_dir / "enriched_log_bloom_only.xes")
                )
            except Exception as e:
                logger.warning(f"Job {job_id}: Bloom XES export skipped: {e}")

        job_manager.update_progress(job_id, 85)

        # Step 7: Create ZIP package
        logger.info(f"Job {job_id}: Creating ZIP package")
        zip_filename = (
            f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        zip_path = TEMP_DIR / f"{job_id}_{zip_filename}"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in output_dir.glob("*"):
                zipf.write(file, arcname=file.name)

        job_manager.update_progress(job_id, 95)

        # Mark job as completed
        job_manager.mark_completed(job_id, zip_path)
        logger.info(f"Job {job_id}: Processing completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Processing failed: {str(e)}", exc_info=True)
        job_manager.mark_failed(job_id, str(e))

    finally:
        # ALWAYS delete input file after processing (success or failure)
        input_path = Path(input_file)
        if input_path.exists():
            try:
                input_path.unlink()
                logger.debug(f"Job {job_id}: Deleted input file")
            except Exception as e:
                logger.warning(f"Job {job_id}: Failed to delete input: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
