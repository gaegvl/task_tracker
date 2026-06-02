from fastapi import FastAPI
from typing import AsyncGenerator
from src.presentation.api.routers import health, tasks, projects
from src.infrastructure.config import get_settings
from src.infrastructure.db.engine import create_engine
from src.infrastructure.db.session import create_session_factory


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(projects.router)
