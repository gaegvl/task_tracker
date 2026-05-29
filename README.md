# Task Tracker

REST API для задач: создание, список с фильтрами, получение и обновление. Проект построен по слоям (domain → application → infrastructure → presentation) с портами и use case’ами. Данные хранятся в PostgreSQL (async SQLAlchemy + Alembic).

## Стек

- Python 3.14+
- [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/), [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/) + asyncpg
- [Alembic](https://alembic.sqlalchemy.org/) (миграции схемы)
- [pytest](https://pytest.org/), [httpx](https://www.python-httpx.org/) (для `TestClient`)

Управление зависимостями: [uv](https://docs.astral.sh/uv/) (`uv.lock` в репозитории).

## Конфигурация

Скопируй шаблон и задай свои значения:

```bash
cp src/.env.example src/.env
```

В `src/.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1:5432/task_tracker_dev
TEST_DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1:5432/task_tracker_test
```

- `DATABASE_URL` — приложение (`uvicorn`)
- `TEST_DATABASE_URL` — pytest (подменяется в `tests/conftest.py`)

Файл `src/.env` в git не коммитится.

## Установка

```bash
cd /path/to/task_tracker
uv sync
```

Dev-зависимости (в т.ч. `httpx`):

```bash
uv sync --group dev
```

## Миграции (Alembic)

Схему БД поднимает **Alembic**, не приложение. Перед первым запуском и после pull с новыми ревизиями:

```bash
uv run alembic upgrade head
```

Полезные команды:

| Команда | Назначение |
|---------|------------|
| `uv run alembic current` | Текущая ревизия |
| `uv run alembic history` | История ревизий |
| `uv run alembic revision --autogenerate -m "описание"` | Новая миграция (проверь файл вручную) |
| `uv run alembic downgrade -1` | Откат на одну ревизию |

Если autogenerate сгенерировал `drop_table` вместо `create_table` на пустой БД — ревизию нужно поправить вручную.

## Запуск сервера

```bash
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

По умолчанию: `http://127.0.0.1:8000`. Документация: [Swagger UI](http://127.0.0.1:8000/docs), [ReDoc](http://127.0.0.1:8000/redoc).

## API

| Метод | Путь | Описание |
|--------|------|----------|
| `GET` | `/health` | Проверка живости: `{"status": "ok"}` |
| `POST` | `/tasks/` | Создать задачу |
| `GET` | `/tasks/` | Список задач (фильтры, пагинация) |
| `GET` | `/tasks/{task_id}` | Получить задачу по UUID |
| `PATCH` | `/tasks/{task_id}` | Обновить задачу (частично) |

Статусы: `todo`, `in_progress`, `done`.

### Создание задачи (`POST /tasks/`)

Тело (JSON): `title`, `description` (optional), `project_id` (UUID).

Ответ `201`: `id`, `title`, `status` (по умолчанию `todo`), `created_at`. Невалидный `title` → `400`.

### Список (`GET /tasks/`)

Query: `project_id` (обязательный), `status` (optional), `limit` (1–100, default 20), `offset` (≥ 0, default 0).

Ответ `200`: массив `TaskResponse`, сортировка `created_at` desc. Ошибки валидации → `422`.

### Получение (`GET /tasks/{task_id}`)

Ответ `200` или `404` (`{"detail": "Task not found"}`).

### Обновление (`PATCH /tasks/{task_id}`)

Тело: `status` (обязательный), `title`, `description`, `project_id` (optional). Ответ `200` или `404`. Невалидный enum → `422`.

### Примеры (curl)

```bash
# создать
curl -s -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"My task","project_id":"550e8400-e29b-41d4-a716-446655440000"}'

# список todo в проекте
curl -s "http://127.0.0.1:8000/tasks/?project_id=550e8400-e29b-41d4-a716-446655440000&status=todo"

# сменить статус
curl -s -X PATCH "http://127.0.0.1:8000/tasks/<TASK_ID>" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}'
```

## Тесты

Перед pytest: миграции на test-базу (делает `tests/conftest.py` автоматически), затем `TRUNCATE` перед каждым тестом.

```bash
uv run pytest
```

Unit-тесты use case используют `InMemoryTaskRepository` без Postgres. API-тесты — `TestClient` + `TEST_DATABASE_URL`.

## Структура каталогов

```
src/
  domain/
  application/
  infrastructure/   # config, engine, ORM, репозитории
  presentation/
  main.py
alembic/            # env.py, versions/
tests/
learning_steps/
```
