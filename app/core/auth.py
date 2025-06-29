from typing import Any, TypedDict, cast
from urllib.parse import urlencode

import httpx

from app.config import get_settings

settings = get_settings()


class UserProfile(TypedDict):
    id: str
    email: str
    name: str
    picture: str | None


class AccessTokenError(Exception):
    """Custom exception for access token retrieval errors."""


class UserProfileError(Exception):
    """Custom exception for user profile retrieval errors."""


class GoogleOAuth2Provider:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_redirect_uri(self) -> str:
        """Return the redirect URI for Google OAuth2."""

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
        }
        query_string = urlencode(params)
        return f"https://accounts.google.com/o/oauth2/auth?{query_string}"

    async def get_access_token(self, code: str) -> str:
        """Get access token from Google using the authorization code."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise AccessTokenError(f"Failed to retrieve access token: {e.response.text}") from e

        result = cast(dict[str, Any], response.json())
        return str(result["access_token"])

    async def get_profile(self, access_token: str) -> UserProfile:
        """Get user profile information from Google using the access token."""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise UserProfileError(f"Failed to retrieve user profile: {e.response.text}") from e

        result = cast(dict[str, Any], response.json())
        return UserProfile(
            id=result["id"],
            email=result["email"],
            name=result["name"],
            picture=result.get("picture"),
        )
