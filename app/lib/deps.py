from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.domains.users.schemas import User
from app.domains.users.services import UserService, provide_users_service


async def get_current_user(
    request: Request, user_service: Annotated[UserService, Depends(provide_users_service)]
) -> User:
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID missing in cookie",
        )

    user = await user_service.get_one_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user_service.to_schema(user, schema_type=User)
