import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class OutputFormat(StrEnum):
    """Enumeration for output formats of generated images."""

    PNG = "png"
    JPG = "jpg"


class Ratio(StrEnum):
    """Enumeration for aspect ratios of generated images."""

    RATIO_1_1 = "1:1"
    RATIO_16_9 = "16:9"
    RATIO_4_3 = "4:3"


class Status(StrEnum):
    """Enumeration for the status of a generation request."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(kw_only=True)
class User:
    """Data class representing a user."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    google_id: str = field()
    email: str = field()
    name: str = field()
    picture: str | None = field()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = field(default=None)


@dataclass(kw_only=True)
class Generation:
    """Data class representing a generation request."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field()
    prompt: str = field()
    status: Status = field(default=Status.PENDING)
    output_format: OutputFormat = field(default=OutputFormat.PNG)
    ratio: Ratio = field(default=Ratio.RATIO_1_1)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    image_path: str | None = field(default=None)
