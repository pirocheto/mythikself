from datetime import UTC, datetime
from typing import Annotated, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.config import get_settings
from app.db.models import UserORM
from app.mappers import user_mapper
from app.models import User
from app.schemas import UserProfile

settings = get_settings()

router = APIRouter()


@router.get("/login/google")
def login_via_google(request: Request) -> RedirectResponse:
    """Redirects the user to the Google authentication page."""

    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
        "scope": "openid email profile",
    }
    query_string = urlencode(params)
    google_redirect_url = f"https://accounts.google.com/o/oauth2/auth?{query_string}"
    return RedirectResponse(url=google_redirect_url)


@router.get("/auth/google/callback")
async def auth_via_google(
    request: Request, code: str, session: Annotated[AsyncSession, Depends(get_db)]
) -> RedirectResponse:
    """Handles the callback from Google after user authentication."""

    # =============== Get access token ================
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
            },
        )

    if token_response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to obtain access token",
        )

    response_data = token_response.json()
    access_token = response_data["access_token"]

    # =============== Get user info ==================
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if user_info_response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to obtain user information",
        )
    user_info = user_info_response.json()

    # =============== Check if user exists and create if not ================
    async with session.begin():
        # Check if user already exists in the database
        statement = select(UserORM).where(UserORM.google_id == user_info.get("id"))
        result = await session.execute(statement)
        user_orm = result.scalars().one_or_none()

        if not user_orm:
            # If user does not exist, create a new user
            user = User(
                google_id=user_info["id"],
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info.get("picture"),
                last_login=datetime.now(UTC),
            )
            user_orm = user_mapper.domain_to_orm(user)
            session.add(user_orm)
        else:
            # If user exists, update the user information
            user_orm.email = user_info["email"]
            user_orm.name = user_info["name"]
            user_orm.picture = user_info.get("picture")
            user_orm.last_login = datetime.now(UTC)

        user_id = user_orm.id

    # =============== Set user ID in cookie and redirect ================
    response = RedirectResponse("/users/profile")
    response.set_cookie(
        key="user_id",
        value=str(user_id),
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="lax",
    )
    return response


@router.get("/users/profile", response_model=UserProfile)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    return current_user
