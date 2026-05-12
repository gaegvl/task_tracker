from fastapi import FastAPI
from typing import AsyncGenerator
from src.presentation.api.routers import health, tasks
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task_repository = InMemoryTaskRepository()
    app.state.task_repository = task_repository
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(tasks.router)
