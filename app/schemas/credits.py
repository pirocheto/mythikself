from pydantic import BaseModel


class CreditResponse(BaseModel):
    """Schema for the response when credits are added to a user's account."""

    message: str
