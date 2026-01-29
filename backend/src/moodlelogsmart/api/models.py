"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class UploadResponse(BaseModel):
    """Response from upload endpoint."""

    job_id: str = Field(..., description="Unique job identifier (UUID)")
    status: Literal["processing", "completed", "failed"] = Field(
        default="processing", description="Current job status"
    )
    message: str = Field(default="File uploaded and processing started")


class StatusResponse(BaseModel):
    """Response from status endpoint."""

    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["processing", "completed", "failed"] = Field(
        ..., description="Current job status"
    )
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage (0-100)")
    error: Optional[str] = Field(default=None, description="Error message if status is failed")
    created_at: Optional[datetime] = Field(default=None, description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")


class DownloadResponse(BaseModel):
    """Response for download endpoint (file served directly, not JSON)."""

    pass  # File served directly with application/zip MIME type


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
