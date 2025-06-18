from collections.abc import AsyncGenerator

from advanced_alchemy.extensions.fastapi import repository, service

from app.db.deps import DatabaseSession
from app.db.models import UserORM


class UserService(service.SQLAlchemyAsyncRepositoryService[UserORM]):
    """User service."""

    class Repo(repository.SQLAlchemyAsyncRepository[UserORM]):
        """User repository."""

        model_type = UserORM

    repository_type = Repo


async def provide_users_service(db_session: DatabaseSession) -> AsyncGenerator[UserService]:
    """This provides an instance of UserService with a database session."""
    async with UserService.new(session=db_session) as service:
        yield service
