# Task Tracker

![CI](https://github.com/gaegvl/task_tracker/actions/workflows/ci.yaml/badge.svg)

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

## API Задач

| Метод | Путь | Описание |
|--------|------|----------|
| `GET` | `/health` | Проверка живости: `{"status": "ok"}` |
| `POST` | `/tasks/` | Создать задачу |
| `GET` | `/tasks/` | Список задач (фильтры, пагинация) |
| `GET` | `/tasks/{task_id}` | Получить задачу по UUID |
| `PATCH` | `/tasks/{task_id}` | Обновить задачу (частично) |
| `DELETE` | `/tasks/{task_id}` | Удалить задачу |
| `POST` | `/tasks/{task_id}/restore` | Восстановить задачу |
| `GET` | `/tasks/{task_id}/status-history` | Список смен статуса задачи (пагинация) |
| `DELETE` | `/tasks/{task_id}/purge` | Удалить задачу (необратимо) |

Статусы: `todo`, `in_progress`, `done`.

### Создание задачи (`POST /tasks/`)

Тело (JSON): `title`, `description` (optional), `project_id` (UUID).

Ответ `201`: `id`, `title`, `status` (по умолчанию `todo`), `created_at`. Невалидный `title` → `400`.

### Список задач (`GET /tasks/`)

Query: `project_id` (обязательный), `status` (optional), `limit` (1–100, default 20), `offset` (≥ 0, default 0).

Ответ `200`: массив `TaskResponse`, сортировка `created_at` desc. Ошибки валидации → `422`.

### Получение задачи по id (`GET /tasks/{task_id}`)

Ответ `200` или `404` (`{"detail": "Task not found"}`).

### Обновление задачи по id (`PATCH /tasks/{task_id}`)

Body: `status` (обязательный), `title`, `description`, `project_id` (optional).
Допустимые переходы статуса: 
- `todo` -> `in_progress` -> `done`.
- `in_progress` -> `todo`.
- `in_progress` -> `done`.
- `same -> same` ✅ (разрешить идемпотентный PATCH)
Ответ `200` или `404`. 
Невалидный enum → `422`.
Невалидный переход статуса -> `409` + ожидаемый `detail` ("Invalid task status transition").

### Удаление задачи по id (логическое) (`DELETE /tasks/{task_id}`)

Данные остаются в бд с полем deleted_at, которое устанавливается в текущую дату и время.
Path: `task_id` (обязательный). Ответ `204` или `404`. Ошибки валидации → `422`.

### Удаление задачи по id (необратимое) (`DELETE /tasks/{task_id}/purge`)
Удаляет задачу необратимо. Удаление возможно только для soft-deleted задач.
Path: `task_id` (обязательный). Ответ `204` или `404`. Ошибки валидации → `422`.

### Восстановление задачи по id (`POST /tasks/{task_id}/restore`)
Восстанавливает soft-deleted задачу. Активный проект не затрагивается. Если проект удален(soft-deleted), то восстановление невозможно.
Path: `task_id` (обязательный).
Ответ `200` или `404`. Ошибки валидации → `422`.

### Список смен статуса задачи (`GET /tasks/{task_id}/status-history`)
Изменения статуса задачи записываются в историю, только при реальной смене статуса через PATCH.

Query: `limit` (1–100, default 10), `offset` (≥ 0, default 0).

Ответ `200`: массив `TaskStatusChangeResponse`. Ошибки валидации → `422`. Задача не найдена → `404`.

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

# невалидный переход статуса -> 409
curl -s -X PATCH "http://127.0.0.1:8000/tasks/<TASK_ID>" \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}'

# удалить
curl -s -X DELETE "http://127.0.0.1:8000/tasks/<TASK_ID>"

# несуществующая задача
curl -s -X GET "http://127.0.0.1:8000/tasks/<TASK_ID>"

# восстановить задачу
curl -s -X POST "http://127.0.0.1:8000/tasks/<TASK_ID>/restore"

# список смен статуса задачи
curl -s "http://127.0.0.1:8000/tasks/<TASK_ID>/status-history?limit=10&offset=0"

# удалить задачу необратимо
curl -s -X DELETE "http://127.0.0.1:8000/tasks/<TASK_ID>/purge"

```

## API Проектов

| Метод | Путь | Описание |
|--------|------|----------|
| `POST` | `/projects/` | Создать проект |
| `GET` | `/projects/` | Список проектов (пагинация) |
| `GET` | `/projects/{project_id}` | Получить проект по UUID |
| `PATCH` | `/projects/{project_id}` | Обновить проект (частично) |
| `DELETE` | `/projects/{project_id}` | Удалить проект |
| `POST` | `/projects/{project_id}/restore` | Восстановить проект |
| `DELETE` | `/projects/{project_id}/purge` | Удалить проект (необратимо) |

### Создание проекта (`POST /projects/`)

Тело (JSON): `name`, `description` (optional).

Ответ `201`: `id`, `name`, `description`, `created_at`. Невалидный `name` → `400`.

### Список проектов (`GET /projects/`)

Query: `limit` (1–100, default 10), `offset` (≥ 0, default 0).

Ответ `200`: массив `CreateProjectResponse`. Ошибки валидации → `422`.

### Получение проекта по id (`GET /projects/{project_id}`)

Ответ `200` или `404` (`{"detail": "Project not found"}`).

### Обновление проекта по id (`PATCH /projects/{project_id}`)

Body: `name`, `description` (optional). Ответ `200` или `404`. Невалидный `name` → `400`.

### Удаление проекта по id (логическое) (`DELETE /projects/{project_id}`)

Данные остаются в бд с полем deleted_at, которое устанавливается в текущую дату и время.
Path: `project_id` (обязательный). Ответ `204` или `404`. Ошибки валидации → `422`. Если есть активные задачи -> `409` + ожидаемый `detail` ("Project has tasks").

### Восстановление проекта по id (`POST /projects/{project_id}/restore`)
Восстанавливает soft-deleted проект и все его soft-deleted задачи (каскадно). Активные задачи не затрагиваются. Восстановление возможно только для soft-deleted проектов.

Path: `project_id` (обязательный).
Ответ `200` или `404`. Ошибки валидации → `422`.

### Удаление проекта по id (необратимое) (`DELETE /projects/{project_id}/purge`)
Удаляет проект необратимо. Удаление возможно только для soft-deleted проектов. Каскадное удаление (soft-deleted) задач. 
Path: `project_id` (обязательный). Ответ `204` или `404`. Ошибки валидации → `422`. Если есть активные задачи (защита от неконсистентности данных) -> `409` + ожидаемый `detail` ("Project has tasks").

### Примеры (curl)

```bash
# создать
curl -s -X POST http://127.0.0.1:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name":"My project","description":"My description"}'

# список проектов
curl -s "http://127.0.0.1:8000/projects/?limit=10&offset=0"

# получить проект по id
curl -s "http://127.0.0.1:8000/projects/<PROJECT_ID>"

# обновить проект
curl -s -X PATCH "http://127.0.0.1:8000/projects/<PROJECT_ID>" \
  -H "Content-Type: application/json" \
  -d '{"name":"My project","description":"My description"}'

# удалить
curl -s -X DELETE "http://127.0.0.1:8000/projects/<PROJECT_ID>"

# восстановить проект
curl -s -X POST "http://127.0.0.1:8000/projects/<PROJECT_ID>/restore"

# удалить проект необратимо
curl -s -X DELETE "http://127.0.0.1:8000/projects/<PROJECT_ID>/purge"
```


## Тесты

Перед pytest: миграции на test-базу (делает `tests/conftest.py` автоматически), затем `TRUNCATE` перед каждым тестом.

```bash
uv run pytest
```

Unit-тесты use case используют `InMemoryTaskRepository` без Postgres. API-тесты — `TestClient` + `TEST_DATABASE_URL`.

## Линтеры

uv sync --group dev

uv run ruff check .
uv run ruff format --check .
uv run mypy src

## Pre-commit

uv sync --group dev
uv run pre-commit install

# проверить все файлы вручную
uv run pre-commit run --all-files

## CI

На каждый push и pull request [GitHub Actions](https://github.com/features/actions) запускает:
- `ruff check .` и `ruff format --check .`
- `mypy src`
- `pytest` (с PostgreSQL в service container)

Статус последнего прогона: вкладка **Actions** в репозитории на GitHub.

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
```
