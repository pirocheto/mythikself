import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum, String


class Base(DeclarativeBase):
    pass


class OutputFormat(StrEnum):
    PNG = "png"
    JPG = "jpg"


class Ratio(StrEnum):
    RATIO_1_1 = "1:1"
    RATIO_16_9 = "16:9"
    RATIO_4_3 = "4:3"


class Status(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class UserORM(Base):
    """
    User model representing a user in the system.
    Inherits from UUIDAuditBase for UUID primary key and audit fields.
    """

    __tablename__ = "users"

    # Fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    picture: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(UTC))
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    generations: Mapped[list["GenerationORM"]] = relationship(
        "GenerationORM", back_populates="user", cascade="all, delete-orphan"
    )


class GenerationORM(Base):
    """
    Generation model representing a generation in the system.
    Inherits from UUIDAuditBase for UUID primary key and audit fields.
    """

    __tablename__ = "generations"

    # Fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(UTC))
    output_format: Mapped[OutputFormat] = mapped_column(Enum(OutputFormat), nullable=False)
    ratio: Mapped[Ratio] = mapped_column(Enum(Ratio), nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)

    # Relationships
    user: Mapped[UserORM] = relationship("UserORM", back_populates="generations")
