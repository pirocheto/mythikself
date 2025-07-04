from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.types import UUID4

from app.db.models import ContentType, OutputFormat, Ratio, Status


class GenerationData(BaseModel):
    """Schema for a generation request."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    prompt: str
    created_at: datetime
    status: Status
    output_format: OutputFormat
    size: int | None = None
    content_type: ContentType | None = None
    ratio: Ratio
    filename: str | None = None
    preview_url: str | None = None


class GenerationList(BaseModel):
    """Schema for a list of generations."""

    count: int
    data: list[GenerationData]


class GenerationStatus(BaseModel):
    """Schema for the status of a generation request."""

    id: UUID4
    status: Status
    error_message: str | None = None


class GenerationCreateResponse(BaseModel):
    """Schema for the response of a generation creation request."""

    message: str
    generation_id: UUID4


class DownloadURLResponse(BaseModel):
    """Schema for the response containing a download URL."""

    url: str
    filename: str
    content_type: ContentType
    size: int
    expires_in: int
