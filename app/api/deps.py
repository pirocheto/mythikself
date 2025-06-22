import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.config import engine
from app.db.models import UserORM
from app.mappers import user_mapper
from app.models import User

settings = get_settings()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session


async def get_current_user(
    user_id: Annotated[uuid.UUID, Cookie()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
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

        user = user_mapper.orm_to_domain(user_orm)

    return user
