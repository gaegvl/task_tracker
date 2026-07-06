from fastapi.testclient import TestClient

from src.infrastructure.db.seed_users import ADMIN_USER_ID, USER_USER_ID
from src.main import app
from tests.helpers import (
    ADMIN_API_KEY,
    admin_headers,
    create_project_via_api,
    create_task_via_api,
    user_headers,
)


def test_restore_task_without_auth_returns_401() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id}")

        response = client.post(f"/tasks/{task_id}/restore")

        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}


def test_restore_task_with_invalid_api_key_returns_401() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id}")

        response = client.post(
            f"/tasks/{task_id}/restore",
            headers={"Authorization": "Bearer wrong-key"},
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API key"}


def test_restore_task_with_user_key_returns_403() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id}")

        response = client.post(f"/tasks/{task_id}/restore", headers=user_headers())

        assert response.status_code == 403
        assert response.json() == {"detail": "Admin access required"}


def test_restore_task_with_admin_key_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id}")

        response = client.post(f"/tasks/{task_id}/restore", headers=admin_headers())

        assert response.status_code == 200


def test_purge_task_with_user_key_returns_403() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id}")

        response = client.delete(f"/tasks/{task_id}/purge", headers=user_headers())

        assert response.status_code == 403
        assert response.json() == {"detail": "Admin access required"}


def test_purge_project_without_auth_returns_401() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")

        response = client.delete(f"/projects/{project_id}/purge")

        assert response.status_code == 401


def test_restore_project_with_admin_key_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")

        response = client.post(
            f"/projects/{project_id}/restore", headers=admin_headers()
        )

        assert response.status_code == 200


def test_create_task_without_auth_still_works() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        response = client.post(
            "/tasks",
            json={
                "title": "Public task",
                "description": "No auth required",
                "project_id": str(project_id),
            },
        )

        assert response.status_code == 201


def test_restore_task_without_bearer_prefix_returns_401() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id}")

        response = client.post(
            f"/tasks/{task_id}/restore",
            headers={"Authorization": ADMIN_API_KEY},
        )

        assert response.status_code == 401


def test_update_task_with_user_key_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        response = client.patch(
            f"tasks/{task_id}",
            headers=user_headers(),
            json={"status": "in_progress"},
        )
        assert response.status_code == 200

        response = client.get(f"tasks/{task_id}/status-history")
        assert response.json()[0]["changed_by"] == str(USER_USER_ID)


def test_update_task_with_admin_key_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        response = client.patch(
            f"tasks/{task_id}",
            headers=admin_headers(),
            json={"status": "in_progress"},
        )

        assert response.status_code == 200
        response = client.get(f"tasks/{task_id}/status-history")
        assert response.json()[0]["changed_by"] == str(ADMIN_USER_ID)


def test_update_task_without_api_key_sets_changed_by_null() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        response = client.patch(
            f"tasks/{task_id}",
            json={"status": "in_progress"},
        )

        assert response.status_code == 200
        response = client.get(f"tasks/{task_id}/status-history")
        assert response.json()[0]["changed_by"] is None


def test_update_task_with_invalid_api_key_returns_401() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id = create_task_via_api(client, project_id)
        response = client.patch(
            f"tasks/{task_id}",
            headers={"Authorization": "Bearer invalid-key"},
            json={"status": "in_progress"},
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API key"}
