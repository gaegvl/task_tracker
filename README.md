# Task Tracker

REST API для задач: создание и получение по идентификатору. Проект построен по слоям (domain → application → infrastructure → presentation) с портами и use case’ами; данные пока хранятся в памяти на время жизни процесса.

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
| `GET` | `/tasks/{task_id}` | Получить задачу по UUID |

### Создание задачи (`POST /tasks/`)

Тело запроса (JSON):

- `title` (string) — непустой, минимум 3 символа после обрезки пробелов;
- `description` (string, optional);
- `project_id` (UUID).

Ответ `201`: `id`, `title`, `status` (по умолчанию `todo`), `created_at`.

При невалидном заголовке — `400` с текстом `Invalid task title`.

### Получение задачи (`GET /tasks/{task_id}`)

Ответ `200`: поля задачи, включая `description` и `project_id`.

Если задачи нет — `404`, тело: `{"detail": "Task not found"}`.

## Тесты

Из корня репозитория (в `pyproject.toml` задан `pythonpath = ["."]`):

```bash
uv run pytest
```

## Структура каталогов

```
src/
  domain/           # сущности, статусы, доменные исключения
  application/    # порты, use case’ы
  infrastructure/ # реализации (сейчас in-memory репозиторий)
  presentation/   # FastAPI: роутеры, схемы, зависимости
  main.py         # точка входа, lifespan, подключение роутеров
tests/              # pytest
learning_steps/     # пошаговые заметки по развитию проекта
```

Данные не сохраняются между перезапусками сервера: используется `InMemoryTaskRepository`, создаётся в `lifespan` приложения.
