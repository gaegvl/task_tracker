from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import create_project_via_api, create_task_via_api


def test_get_task_status_history_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
        response = client.get(f"/tasks/{task_id}/status-history")
        assert response.status_code == 200
        assert len(response.json()) == 1
        client.patch(f"/tasks/{task_id}", json={"status": "done"})
        response = client.get(f"/tasks/{task_id}/status-history")
        assert len(response.json()) == 2


def test_task_status_history_update_task_title_without_status_change() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.patch(
            f"/tasks/{task_id}", json={"title": "Test Task 2", "status": "todo"}
        )
        response = client.get(f"/tasks/{task_id}/status-history")
        assert len(response.json()) == 0


def test_task_status_history_status_change_to_the_same_status() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
        response = client.get(f"/tasks/{task_id}/status-history")
        assert len(response.json()) == 1
        client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
        response = client.get(f"/tasks/{task_id}/status-history")
        assert len(response.json()) == 1


def test_task_status_history_invalid_status_transition() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.patch(f"/tasks/{task_id}", json={"status": "done"})
        response = client.get(f"/tasks/{task_id}/status-history")
        assert len(response.json()) == 0


def test_task_status_history_returns_404_when_task_not_found() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/tasks/123e4567-e89b-12d3-a456-426614174000/status-history"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}


def test_task_status_history_returns_404_after_task_is_deleted() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
        response = client.get(f"/tasks/{task_id}/status-history")
        assert len(response.json()) == 1
        client.delete(f"/tasks/{task_id}")
        response = client.get(f"/tasks/{task_id}/status-history")
        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}
