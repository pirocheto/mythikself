import logging
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

root_dir = Path(__file__).resolve().parents[1]  # Adjust to your project structure


logger = logging.getLogger(__name__)


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from a string or list of strings."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # Use top level .env file (one level above ./backend/)
    model_config = SettingsConfigDict(
        env_file=root_dir / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_dir: Path = root_dir / "app"
    """The root directory of the application, used for file paths."""

    SECRET_KEY: str = secrets.token_urlsafe(32)
    """The secret key used for encoding and decoding JWT tokens."""

    FRONTEND_HOST: str = "http://localhost:5173"
    """The host for the frontend application, used for emails and redirects."""

    BACKEND_HOST: str = "http://localhost:8000"
    """The host for the backend application, used for documentation"""

    # The environment the application is running in
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    """The environment the application is running in, used for configuration."""

    # Allow backend to be accessed from given origins
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []
    """The CORS origins allowed for the backend application."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Add the frontend host to the backend CORS origins
        """
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    PROJECT_NAME: str = "App"
    """The name of the project, used in emails and documentation."""

    POSTGRES_SERVER: str
    """The server address for the PostgreSQL database."""
    POSTGRES_PORT: int = 5432
    """The port for the PostgreSQL database."""
    POSTGRES_USER: str
    """The username for the PostgreSQL database."""
    POSTGRES_PASSWORD: str = ""
    """The password for the PostgreSQL database."""
    POSTGRES_DATABASE: str = ""
    """The name of the PostgreSQL database."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DATABASE,
        )

    # The API key for the Resend service
    RESEND_API_KEY: str | None = None
    """The API key for the Resend service, used for sending emails."""

    EMAILS_TEST_RECIPIENT: EmailStr = "test@example.com"
    """The email address to send test emails to"""
    EMAILS_FROM_EMAIL: EmailStr | None = None
    """The email address of the sender of the emails"""
    EMAILS_FROM_NAME: str | None = None
    """The name of the sender of the emails"""

    REPLICATE_API_KEY: str = "your-replicate-api-key"
    """The API key for the Replicate service, used for AI model inference."""

    GOOGLE_OAUTH2_CLIENT_ID: str = "your-google-client-id"
    """Google OAuth2 client ID for authentication."""
    GOOGLE_OAUTH2_CLIENT_SECRET: str = "your-google-client-secret"
    """Google OAuth2 client secret for authentication."""
    GOOGLE_OAUTH2_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    """Google OAuth2 redirect URI for authentication."""

    SCW_ACCESS_KEY: str = "your-scaleway-access-key"
    """Your Scaleway access key."""
    SCW_SECRET_KEY: str = "your-scaleway-secret-key"
    """Your Scaleway secret key."""
    S3_BUCKET_NAME: str = "your-bucket"
    """The name of the S3 bucket where files will be stored."""
    S3_BUCKET_ENDPOINT: str = "https://s3.example.com"
    """The endpoint URL for the S3 storage, e.g., https://s3.example.com"""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def S3_BUCKET_URL(self) -> str:
        """
        Construct the full URL for the S3 bucket.
        This is used to access files stored in the bucket.
        """
        return f"{self.S3_BUCKET_ENDPOINT}/{self.S3_BUCKET_NAME}"

    REDIS_HOST: str = "localhost"
    """The host for the Redis server."""
    REDIS_PORT: int = 6379
    """The port for the Redis server."""

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @property
    @computed_field
    def emails_enabled(self) -> bool:
        """Check if email sending is enabled"""
        return bool(self.RESEND_API_KEY and self.EMAILS_FROM_EMAIL)


@lru_cache
def get_settings() -> Settings:
    """
    Get settings with caching
    This is used to avoid reloading the settings
    every time they are accessed.
    """
    return Settings()  # type: ignore
