"""Input validation utilities for API security."""

import csv
import io
import uuid
from typing import Tuple
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Validation limits
MAX_COLUMNS = 100  # Prevent memory bomb
MAX_ROWS_PREVIEW = 10000  # Check first 10k rows


def validate_csv_content(content: bytes) -> Tuple[bool, str]:
    """Validate CSV file structure and content.

    Args:
        content: CSV file bytes

    Returns:
        (is_valid, error_message)

    Raises:
        HTTPException: If CSV is malformed or suspicious
    """
    try:
        # Decode and check if valid UTF-8
        text = content.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        raise HTTPException(400, "File encoding must be UTF-8")

    # Use CSV sniffer to detect format
    try:
        sample = text[:4096]  # First 4KB
        csv.Sniffer().sniff(sample)
    except csv.Error as e:
        raise HTTPException(400, f"Invalid CSV format: {str(e)}")

    # Parse and validate structure
    try:
        reader = csv.reader(io.StringIO(text))
        header = next(reader, None)

        if not header:
            raise HTTPException(400, "CSV file is empty")

        # Check column count
        if len(header) > MAX_COLUMNS:
            raise HTTPException(
                400,
                f"Too many columns ({len(header)}), max {MAX_COLUMNS}"
            )

        # Check for suspicious patterns (CSV injection)
        for field in header:
            if field.startswith(('=', '+', '-', '@', '\t', '\r')):
                raise HTTPException(
                    400,
                    "CSV contains potentially unsafe formula characters"
                )

        # Check row count (sample)
        row_count = 1  # Header
        for i, row in enumerate(reader):
            if i >= MAX_ROWS_PREVIEW:
                break
            row_count += 1

            # Validate row has consistent columns
            if len(row) != len(header):
                logger.warning(
                    f"Row {row_count} has {len(row)} columns, "
                    f"expected {len(header)}"
                )

        logger.info(f"CSV validated: {len(header)} columns, ~{row_count} rows")
        return True, ""

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV validation error: {e}")
        raise HTTPException(400, "CSV validation failed")


def validate_job_id(job_id: str) -> str:
    """Validate job ID is a valid UUID.

    Args:
        job_id: Job identifier to validate

    Returns:
        Validated job_id (normalized)

    Raises:
        HTTPException: 400 if invalid UUID
    """
    try:
        # Parse and validate UUID
        parsed = uuid.UUID(job_id)
        # Return normalized form (lowercase, with hyphens)
        return str(parsed)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format. Must be a valid UUID"
        )
