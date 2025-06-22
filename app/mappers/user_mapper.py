from app.db.models import UserORM
from app.models import User


def orm_to_domain(user_orm: UserORM) -> User:
    return User(
        id=user_orm.id,
        google_id=user_orm.google_id,
        name=user_orm.name,
        email=user_orm.email,
        picture=user_orm.picture,
        created_at=user_orm.created_at,
        last_login=user_orm.last_login,
    )


def domain_to_orm(user: User) -> UserORM:
    return UserORM(
        id=user.id,
        google_id=user.google_id,
        name=user.name,
        email=user.email,
        picture=user.picture,
        created_at=user.created_at,
        last_login=user.last_login,
    )
