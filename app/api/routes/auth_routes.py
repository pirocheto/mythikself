from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_google_auth_provider
from app.config import get_settings
from app.core.auth import GoogleOAuth2Provider
from app.db.models import UserORM
from app.schemas.users import UserProfile

settings = get_settings()

router = APIRouter()


@router.get("/login/google")
def login_via_google(
    google_auth_provider: Annotated[GoogleOAuth2Provider, Depends(get_google_auth_provider)],
) -> RedirectResponse:
    """Redirects the user to the Google authentication page."""

    return RedirectResponse(url=google_auth_provider.get_redirect_uri())


@router.get("/auth/google/callback")
async def auth_via_google(
    code: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    google_auth_provider: Annotated[GoogleOAuth2Provider, Depends(get_google_auth_provider)],
) -> RedirectResponse:
    """Handles the callback from Google after user authentication."""

    access_token = await google_auth_provider.get_access_token(code=code)
    user_info = await google_auth_provider.get_profile(access_token)

    async with session.begin():
        statement = select(UserORM).where(UserORM.google_id == user_info.get("id"))
        result = await session.execute(statement)
        user_orm = result.scalars().one_or_none()

        if not user_orm:
            # If user does not exist, create a new user
            user_orm = UserORM(
                google_id=user_info["id"],
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info.get("picture"),
                last_login=datetime.now(UTC),
            )
            session.add(user_orm)
        else:
            # If user exists, update the user information
            user_orm.email = user_info["email"]
            user_orm.name = user_info["name"]
            user_orm.picture = user_info.get("picture")
            user_orm.last_login = datetime.now(UTC)

    response = RedirectResponse("/users/profile")
    response.set_cookie(
        key="user_id",
        value=str(user_orm.id),
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="lax",
    )
    return response


@router.get("/users/profile", response_model=UserProfile)
async def get_profile(current_user: Annotated[UserORM, Depends(get_current_user)]) -> Any:
    """Returns the profile of the currently authenticated user."""
    return current_user
