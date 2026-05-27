import os

import pytest_asyncio
from sqlalchemy import text

from src.infrastructure.config import get_settings, Settings
from src.infrastructure.db.engine import create_engine
from src.infrastructure.db.session import Base, create_session_factory


# Подключаем приложение к test-базе
_settings = Settings()
os.environ["DATABASE_URL"] = _settings.test_database_url
get_settings.cache_clear()
settings = get_settings()


@pytest_asyncio.fixture(autouse=True)
async def _setup_and_clean_db():
    """
    Важно: asyncpg/SQLAlchemy engine нельзя держать через scope="session",
    иначе pytest-asyncio закроет event loop, а пул останется “живым” в другом loop.
    """
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        await session.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
        await session.commit()

    try:
        yield
    finally:
        await engine.dispose()
