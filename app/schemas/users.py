from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class UserProfile(BaseModel):
    """Schema for user profile information."""

    id: UUID4
    email: EmailStr
    name: str
    picture: str
    created_at: datetime
    last_login: datetime | None = None
    credits: int
