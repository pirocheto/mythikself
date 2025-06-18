from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.config import alchemy

DatabaseSession = Annotated[AsyncSession, Depends(alchemy.provide_session())]
