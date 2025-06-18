from advanced_alchemy.extensions.fastapi import AdvancedAlchemy, AsyncSessionConfig, SQLAlchemyAsyncConfig

from app.config.settings import get_settings

settings = get_settings()


sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.SQLALCHEMY_DATABASE_URI,
    session_config=AsyncSessionConfig(expire_on_commit=False),
    create_all=True,
    commit_mode="autocommit",
)

alchemy = AdvancedAlchemy(config=sqlalchemy_config)
