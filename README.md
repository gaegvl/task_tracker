# Task Tracker

REST API для задач: создание, список с фильтрами, получение и обновление. Проект построен по слоям (domain → application → infrastructure → presentation) с портами и use case’ами; данные пока хранятся в памяти на время жизни процесса.

## Стек

- Python 3.14+
- [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/) (зависимость заложена для будущего персистентного слоя)
- [pytest](https://pytest.org/), [httpx](https://www.python-httpx.org/) (для `TestClient`)

Управление зависимостями: [uv](https://docs.astral.sh/uv/) (`uv.lock` в репозитории).

## Установка

```bash
cd /path/to/task_tracker
uv sync
```

Чтобы подтянуть dev-зависимости (в т.ч. `httpx` для тестов API):

```bash
uv sync --group dev
```

## Запуск сервера

```bash
uv run uvicorn src.main:app --reload
```

По умолчанию приложение слушает `http://127.0.0.1:8000`. Интерактивная документация: [Swagger UI](http://127.0.0.1:8000/docs), [ReDoc](http://127.0.0.1:8000/redoc).

## API

| Метод | Путь | Описание |
|--------|------|----------|
| `GET` | `/health` | Проверка живости: `{"status": "ok"}` |
| `POST` | `/tasks/` | Создать задачу |
| `GET` | `/tasks/` | Список задач (фильтры, пагинация) |
| `GET` | `/tasks/{task_id}` | Получить задачу по UUID |
| `PATCH` | `/tasks/{task_id}` | Обновить задачу (частично) |

Статусы задачи: `todo`, `in_progress`, `done`.

### Создание задачи (`POST /tasks/`)

Тело запроса (JSON):

- `title` (string) — непустой, минимум 3 символа после обрезки пробелов;
- `description` (string, optional);
- `project_id` (UUID).

Ответ `201`: `id`, `title`, `status` (по умолчанию `todo`), `created_at`.

При невалидном заголовке — `400` с текстом `Invalid task title`.

### Список задач (`GET /tasks/`)

Query-параметры:

- `project_id` (UUID, **обязательный**) — задачи в рамках проекта;
- `status` (optional) — `todo` | `in_progress` | `done`; без параметра — все статусы;
- `limit` (optional, default `20`) — от 1 до 100;
- `offset` (optional, default `0`) — смещение для пагинации.

Ответ `200`: массив объектов задачи (`TaskResponse`), сортировка по `created_at` (новые первые).

При невалидных `limit` / `offset` или отсутствии `project_id` — `422`.

### Получение задачи (`GET /tasks/{task_id}`)

Ответ `200`: `id`, `title`, `description`, `project_id`, `status`, `created_at`.

Если задачи нет — `404`, тело: `{"detail": "Task not found"}`.

### Обновление задачи (`PATCH /tasks/{task_id}`)

Частичное обновление. Тело запроса (JSON):

- `status` (обязательный) — `todo` | `in_progress` | `done`;
- `title`, `description`, `project_id` (optional) — если не переданы, остаются прежние значения.

Ответ `200`: обновлённая задача (`TaskResponse`).

Если задачи нет — `404`, тело: `{"detail": "Task not found"}`.

При невалидном `status` — `422`.

### Примеры (curl)

Создать задачу:

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"My task","project_id":"550e8400-e29b-41d4-a716-446655440000"}'
```

Список в проекте, только `todo`, первая страница:

```bash
curl -s "http://127.0.0.1:8000/tasks/?project_id=550e8400-e29b-41d4-a716-446655440000&status=todo&limit=20&offset=0"
```

Вторая страница:

```bash
curl -s "http://127.0.0.1:8000/tasks/?project_id=550e8400-e29b-41d4-a716-446655440000&limit=20&offset=20"
```

Сменить статус:

```bash
curl -s -X PATCH "http://127.0.0.1:8000/tasks/<TASK_ID>" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}'
```

## Тесты

Из корня репозитория (в `pyproject.toml` задан `pythonpath = ["."]`):

```bash
uv run pytest
```

## Структура каталогов

```
src/
  domain/           # сущности, статусы, доменные исключения
  application/      # порты, use case’ы
  infrastructure/   # реализации (сейчас in-memory репозиторий)
  presentation/     # FastAPI: роутеры, схемы, зависимости
  main.py           # точка входа, lifespan, подключение роутеров
tests/              # pytest
learning_steps/     # пошаговые заметки по развитию проекта
```

Данные не сохраняются между перезапусками сервера: используется `InMemoryTaskRepository`, создаётся в `lifespan` приложения.
