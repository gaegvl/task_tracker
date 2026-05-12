from fastapi.testclient import TestClient
from src.main import app
from uuid import uuid4


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
