from fastapi.testclient import TestClient
from src.main import app
from uuid import UUID, uuid4
from src.domain.entities.task import TaskStatus


def create_some_tasks(client: TestClient, i: int, project_id: UUID) -> list[UUID]:
    ids = []
    for i in range(i):
        response = client.post(
            "/tasks",
            json={
                "title": f"Test Task {i}",
                "description": f"Test Description {i}",
                "project_id": project_id,
            },
        )
        ids.append(response.json()["id"])
    return ids


def test_post_then_get_task() -> None:
    project_id = str(uuid4())

    with TestClient(app) as client:
        created = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": project_id,
            },
        )

        assert created.status_code == 201
        task_id = created.json()["id"]

        got = client.get(f"/tasks/{task_id}")
        assert got.status_code == 200

        body = got.json()

        assert body["id"] == task_id
        assert body["title"] == "Test Task"
        assert body["description"] == "Test Description"
        assert body["project_id"] == project_id


def test_get_task_by_id_not_found() -> None:
    with TestClient(app) as client:
        got = client.get("/tasks/123e4567-e89b-12d3-a456-426614174000")
        assert got.status_code == 404
        assert got.json() == {"detail": "Task not found"}


def test_get_list_tasks() -> None:
    project_id_todo = str(uuid4())
    project_id_in_progress = str(uuid4())
    with TestClient(app) as client:
        create_some_tasks(client, 15, project_id_todo)
        create_some_tasks(client, 3, project_id_in_progress)

        tasks = client.get(
            "/tasks",
            params={
                "project_id": project_id_todo,
                "status": TaskStatus.TODO.value,
                "limit": 10,
                "offset": 0,
            },
        )
        tasks_json = tasks.json()
        assert tasks.status_code == 200
        assert len(tasks_json) == 10
        assert tasks_json[0]["status"] == TaskStatus.TODO.value

        tasks = client.get(
            "/tasks",
            params={
                "project_id": project_id_todo,
                "status": TaskStatus.TODO.value,
                "limit": 10,
                "offset": 10,
            },
        )
        tasks_json = tasks.json()
        assert tasks.status_code == 200
        assert len(tasks_json) == 5
        assert tasks_json[0]["status"] == TaskStatus.TODO.value

        tasks = client.get(
            "/tasks",
            params={
                "project_id": project_id_in_progress,
                "limit": 10,
                "offset": 0,
            },
        )
        tasks_json = tasks.json()
        assert tasks.status_code == 200
        assert len(tasks_json) == 3
        assert tasks_json[0]["project_id"] == project_id_in_progress


def test_update_task() -> None:
    project_id = str(uuid4())
    with TestClient(app) as client:
        ids = create_some_tasks(client, 3, project_id)

        for i in ids[:2]:
            updated_task = client.patch(
                f"/tasks/{i}",
                json={
                    "status": TaskStatus.IN_PROGRESS.value,
                    "title": "Test Task updated",
                    "description": "Test Description updated",
                    "project_id": project_id,
                },
            )

        assert updated_task.status_code == 200
        assert updated_task.json()["status"] == TaskStatus.IN_PROGRESS.value
        assert updated_task.json()["title"] == "Test Task updated"
        assert updated_task.json()["description"] == "Test Description updated"
        assert updated_task.json()["project_id"] == project_id

        get_task = client.get(f"/tasks/{i}")

        assert get_task.status_code == 200
        assert get_task.json()["status"] == TaskStatus.IN_PROGRESS.value
        assert get_task.json()["title"] == "Test Task updated"

        get_tasks = client.get(
            "/tasks",
            params={
                "project_id": project_id,
                "status": TaskStatus.IN_PROGRESS.value,
                "limit": 10,
                "offset": 0,
            },
        )

        assert len(get_tasks.json()) == 2

        updated_task = client.patch(
            f"/tasks/{uuid4()}",
            json={
                "status": TaskStatus.IN_PROGRESS.value,
                "title": "Test Task updated",
                "description": "Test Description updated",
                "project_id": project_id,
            },
        )
        assert updated_task.status_code == 404
        assert updated_task.json() == {"detail": "Task not found"}
