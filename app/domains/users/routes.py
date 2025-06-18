from typing import Annotated, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.config.settings import get_settings, logger
from app.domains.users.schemas import User, UserProfile
from app.domains.users.services import UserService, provide_users_service
from app.lib.deps import get_current_user

settings = get_settings()

router = APIRouter()


@router.get("/login/google")
async def login_via_google(request: Request) -> Any:
    redirect_uri = str(request.url_for("auth_via_google"))
    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
    }

    query_string = urlencode(params)
    google_redirect_url = f"https://accounts.google.com/o/oauth2/auth?{query_string}"

    return RedirectResponse(url=google_redirect_url)


@router.get("/auth/google/callback")
async def auth_via_google(
    request: Request,
    users_service: Annotated[UserService, Depends(provide_users_service)],
    code: str | None = None,
) -> RedirectResponse:
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No code provided")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": str(request.url_for("auth_via_google")),
            },
        )
    if token_response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=token_response.status_code,
            detail="Failed to obtain access token",
        )

    response_data = token_response.json()
    access_token = response_data["access_token"]

    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"}
        )

    user_info = user_info_response.json()

    user, created = await users_service.get_or_upsert(
        google_id=user_info["id"],
        email=user_info["email"],
        name=user_info.get("name"),
        picture=user_info.get("picture"),
        match_fields=["email"],
        auto_commit=True,
    )

    if created:
        logger.info(f"New user created: {user.email}")

    response = RedirectResponse("/users/profile")
    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="lax",
    )
    return response


@router.get("/users/profile", response_model=UserProfile)
async def get_profile(current_user: Annotated[User, Depends(get_current_user)]) -> Any:
    return current_user
