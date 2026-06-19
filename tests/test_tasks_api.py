from uuid import uuid4

from fastapi.testclient import TestClient

from src.domain.entities.task import TaskStatus
from src.main import app
from tests.helpers import (
    create_project_via_api,
    create_task_via_api,
    create_tasks_via_api,
)


def test_create_task_returns_201() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        response = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": str(project_id),
            },
        )

        assert response.status_code == 201
        assert response.json()["title"] == "Test Task"


def test_get_task_by_id_returns_created_task() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)

        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == task_id
        assert body["title"] == "Test Task"
        assert body["description"] == "Test Description"
        assert body["project_id"] == str(project_id)


def test_get_task_by_id_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/tasks/123e4567-e89b-12d3-a456-426614174000")

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}


def test_list_tasks_filters_by_project_id_and_status() -> None:
    with TestClient(app) as client:
        project_id_todo = create_project_via_api(client, name="Test project_id_todo")
        project_id_other = create_project_via_api(
            client, name="Test project_id_in_progress"
        )
        create_tasks_via_api(client, 15, project_id_todo)
        create_tasks_via_api(client, 3, project_id_other)

        response = client.get(
            "/tasks",
            params={
                "project_id": str(project_id_todo),
                "status": TaskStatus.TODO.value,
                "limit": 10,
                "offset": 0,
            },
        )

        tasks = response.json()
        assert response.status_code == 200
        assert len(tasks) == 10
        assert tasks[0]["status"] == TaskStatus.TODO.value


def test_list_tasks_pagination_offset() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client, name="Test project_id_todo")
        create_tasks_via_api(client, 15, project_id)

        response = client.get(
            "/tasks",
            params={
                "project_id": str(project_id),
                "status": TaskStatus.TODO.value,
                "limit": 10,
                "offset": 10,
            },
        )

        tasks = response.json()
        assert response.status_code == 200
        assert len(tasks) == 5
        assert tasks[0]["status"] == TaskStatus.TODO.value


def test_list_tasks_filters_by_project_id_only() -> None:
    with TestClient(app) as client:
        project_id_todo = create_project_via_api(client, name="Test project_id_todo")
        project_id_other = create_project_via_api(
            client, name="Test project_id_in_progress"
        )
        create_tasks_via_api(client, 15, project_id_todo)
        create_tasks_via_api(client, 3, project_id_other)

        response = client.get(
            "/tasks",
            params={
                "project_id": str(project_id_other),
                "limit": 10,
                "offset": 0,
            },
        )

        tasks = response.json()
        assert response.status_code == 200
        assert len(tasks) == 3
        assert tasks[0]["project_id"] == str(project_id_other)


def test_update_task_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]

        response = client.patch(
            f"/tasks/{task_id}",
            json={
                "status": TaskStatus.IN_PROGRESS.value,
                "title": "Test Task updated",
                "description": "Test Description updated",
                "project_id": str(project_id),
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == TaskStatus.IN_PROGRESS.value
        assert response.json()["title"] == "Test Task updated"
        assert response.json()["description"] == "Test Description updated"
        assert response.json()["project_id"] == str(project_id)


def test_update_task_invalid_status_transition_returns_409() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]

        response = client.patch(
            f"/tasks/{task_id}",
            json={
                "status": TaskStatus.DONE.value,
                "title": "Test Task updated",
                "description": "Test Description updated",
                "project_id": str(project_id),
            },
        )

        assert response.status_code == 409


def test_get_updated_task_returns_new_fields() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]
        client.patch(
            f"/tasks/{task_id}",
            json={
                "status": TaskStatus.IN_PROGRESS.value,
                "title": "Test Task updated",
                "description": "Test Description updated",
                "project_id": str(project_id),
            },
        )

        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200
        assert response.json()["status"] == TaskStatus.IN_PROGRESS.value
        assert response.json()["title"] == "Test Task updated"


def test_list_tasks_filters_by_status_after_update() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_ids = create_tasks_via_api(client, 3, project_id)
        for task_id in task_ids[:2]:
            client.patch(
                f"/tasks/{task_id}",
                json={
                    "status": TaskStatus.IN_PROGRESS.value,
                    "title": "Test Task updated",
                    "description": "Test Description updated",
                    "project_id": str(project_id),
                },
            )

        response = client.get(
            "/tasks",
            params={
                "project_id": str(project_id),
                "status": TaskStatus.IN_PROGRESS.value,
                "limit": 10,
                "offset": 0,
            },
        )

        assert response.status_code == 200
        assert len(response.json()) == 2


def test_update_task_not_found_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        response = client.patch(
            f"/tasks/{uuid4()}",
            json={
                "status": TaskStatus.IN_PROGRESS.value,
                "title": "Test Task updated",
                "description": "Test Description updated",
                "project_id": str(project_id),
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}


def test_delete_task_returns_204() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]

        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code == 204


def test_delete_task_twice_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]
        client.delete(f"/tasks/{task_id}")

        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code == 404


def test_get_deleted_task_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]
        client.delete(f"/tasks/{task_id}")

        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 404


def test_delete_task_not_found_returns_404() -> None:
    with TestClient(app) as client:
        response = client.delete(f"/tasks/{uuid4()}")

        assert response.status_code == 404


def test_create_task_with_invalid_project_id_returns_404() -> None:
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


def test_patch_deleted_task_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task = create_task_via_api(client, project_id)

        client.delete(f"/tasks/{task}")

        response = client.patch(
            f"/tasks/{task}", json={"status": TaskStatus.IN_PROGRESS.value}
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}


def test_delete_task_from_list_tasks() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_ids = create_tasks_via_api(client, 3, project_id)

        client.delete(f"/tasks/{task_ids[0]}")

        response = client.get(
            "/tasks", params={"project_id": str(project_id), "limit": 10, "offset": 0}
        )

        assert response.status_code == 200
        assert len(response.json()) == 2


def test_restore_task_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]
        client.delete(f"/tasks/{task_id}")

        response = client.post(f"/tasks/{task_id}/restore")

        assert response.status_code == 200
        task = client.get(f"/tasks/{task_id}")

        assert task.status_code == 200


def test_restore_task_not_found_returns_404() -> None:
    with TestClient(app) as client:
        response = client.post(f"/tasks/{uuid4()}/restore")

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}


def test_restore_task_active_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]

        response = client.post(f"/tasks/{task_id}/restore")

        assert response.status_code == 404


def test_restore_task_after_delete_and_task_is_in_list_tasks() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_tasks_via_api(client, 1, project_id)[0]
        create_tasks_via_api(client, 3, project_id)
        client.delete(f"/tasks/{task_id}")

        list_task = client.get(
            "/tasks", params={"project_id": str(project_id), "limit": 10, "offset": 0}
        )
        assert len(list_task.json()) == 3
        assert task_id not in [task["id"] for task in list_task.json()]

        response = client.post(f"/tasks/{task_id}/restore")

        assert response.status_code == 200
        task = client.get(f"/tasks/{task_id}")
        assert task.status_code == 200

        list_task = client.get(
            "/tasks", params={"project_id": str(project_id), "limit": 10, "offset": 0}
        )
        assert len(list_task.json()) == 4
        assert task_id in [task["id"] for task in list_task.json()]
