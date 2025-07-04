from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Schema for a generic message response."""

    message: str
