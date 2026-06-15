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
    with TestClient(app) as client:
        create_project = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = create_project.json()["id"]
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
    with TestClient(app) as client:
        project_id_todo = client.post(
            "/projects",
            json={"name": "Test project_id_todo", "description": "Test Description"},
        )
        project_id_in_progress = client.post(
            "/projects",
            json={
                "name": "Test project_id_in_progress",
                "description": "Test Description",
            },
        )
        create_some_tasks(client, 15, project_id_todo.json()["id"])
        create_some_tasks(client, 3, project_id_in_progress.json()["id"])

        tasks = client.get(
            "/tasks",
            params={
                "project_id": project_id_todo.json()["id"],
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
                "project_id": project_id_todo.json()["id"],
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
                "project_id": project_id_in_progress.json()["id"],
                "limit": 10,
                "offset": 0,
            },
        )
        tasks_json = tasks.json()
        assert tasks.status_code == 200
        assert len(tasks_json) == 3
        assert tasks_json[0]["project_id"] == project_id_in_progress.json()["id"]


def test_update_task() -> None:
    with TestClient(app) as client:
        create_project = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = create_project.json()["id"]
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

        updated_task = client.patch(
            f"/tasks/{ids[2]}",
            json={
                "status": TaskStatus.DONE.value,
                "title": "Test Task updated",
                "description": "Test Description updated",
                "project_id": project_id,
            },
        )
        assert updated_task.status_code == 409

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


def test_delete_task() -> None:
    with TestClient(app) as client:
        create_project = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = create_project.json()["id"]
        ids = create_some_tasks(client, 3, project_id)

        assert client.get(f"/tasks/{ids[0]}").status_code == 200

        deleted = client.delete(f"/tasks/{ids[0]}")

        deleted_twice = client.delete(f"/tasks/{ids[0]}")

        assert deleted.status_code == 204
        assert deleted_twice.status_code == 404
        assert client.get(f"/tasks/{ids[0]}").status_code == 404

        assert client.delete(f"/tasks/{uuid4()}").status_code == 404


def test_create_task_with_invalid_project_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": str(uuid4()),
            },
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}
