import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.db.models import OutputFormat, Ratio, Status


@dataclass(kw_only=True)
class User:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    google_id: str = field()
    email: str = field()
    name: str = field()
    picture: str | None = field()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = field(default=None)


@dataclass(kw_only=True)
class Generation:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prompt: str = field()
    status: Status = field(default=Status.PENDING)
    output_format: OutputFormat = field(default=OutputFormat.PNG)
    ratio: Ratio = field(default=Ratio.RATIO_1_1)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
