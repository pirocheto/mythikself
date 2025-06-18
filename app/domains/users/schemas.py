import uuid
from datetime import datetime

from pydantic import EmailStr

from app.lib.schemas import BaseModel


class User(BaseModel):
    """User model for API responses"""

    id: uuid.UUID
    google_id: str
    name: str
    email: EmailStr
    picture: str | None = None
    created_at: datetime
    updated_at: datetime


class UserProfile(BaseModel):
    """User profile model for API responses"""

    name: str
    email: EmailStr
    picture: str | None = None
