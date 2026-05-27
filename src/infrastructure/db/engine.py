from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from src.infrastructure.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
