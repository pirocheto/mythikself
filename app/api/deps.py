import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.auth import GoogleOAuth2Provider
from app.db.config import SessionLocal
from app.db.models import UserORM

settings = get_settings()


async def get_google_auth_provider() -> GoogleOAuth2Provider:
    """Provides an instance of GoogleOAuth2Provider for OAuth2 authentication."""
    return GoogleOAuth2Provider(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_OAUTH2_REDIRECT_URI,
    )


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    user_id: Annotated[uuid.UUID, Cookie()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserORM:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID missing in cookie",
        )

    async with session.begin():
        user_orm = await session.get(UserORM, user_id)

        if not user_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    return user_orm
