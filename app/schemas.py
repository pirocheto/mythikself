import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    """Schema for user profile information."""

    id: uuid.UUID
    email: EmailStr
    name: str
    picture: str
    created_at: datetime
    last_login: datetime | None = None


class GenerationData(BaseModel):
    """Schema for a generation request."""

    id: uuid.UUID
    user_id: uuid.UUID
    prompt: str
    created_at: datetime
    status: str
    output_format: str
    ratio: str


class GenerationList(BaseModel):
    """Schema for a list of generations."""

    count: int
    data: list[GenerationData]


class GenerationCreateResponse(BaseModel):
    """Schema for the response of a generation creation request."""

    message: str
    generation_id: uuid.UUID
