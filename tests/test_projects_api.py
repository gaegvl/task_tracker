from uuid import uuid4

from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import (
    create_project_via_api,
    create_task_via_api,
)


def test_create_project_returns_201() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )

        assert response.status_code == 201
        assert response.json()["id"] is not None
        assert response.json()["name"] == "Test Project"
        assert response.json()["description"] == "Test Description"
        assert response.json()["created_at"] is not None


def test_create_task_for_project_returns_201() -> None:
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
        assert response.json()["id"] is not None
        assert response.json()["title"] == "Test Task"


def test_get_project_by_id_returns_project() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        response = client.get(f"/projects/{project_id}")

        assert response.status_code == 200
        assert response.json()["id"] == project_id
        assert response.json()["name"] == "Test Project"
        assert response.json()["description"] == "Test Description"
        assert response.json()["created_at"] is not None


def test_get_project_by_id_not_found() -> None:
    with TestClient(app) as client:
        response = client.get(f"/projects/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}


def test_list_projects_returns_created_project() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        response = client.get("/projects")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": project_id,
                "name": "Test Project",
                "description": "Test Description",
                "created_at": response.json()[0]["created_at"],
            }
        ]


def test_update_project_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        response = client.patch(
            f"/projects/{project_id}",
            json={"name": "Updated Project", "description": "Updated Description"},
        )

        assert response.status_code == 200
        assert response.json()["id"] == project_id
        assert response.json()["name"] == "Updated Project"
        assert response.json()["description"] == "Updated Description"


def test_update_project_not_found() -> None:
    with TestClient(app) as client:
        response = client.patch(
            f"/projects/{uuid4()}",
            json={"name": "Updated Project", "description": "Updated Description"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}


def test_delete_project_returns_204() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        response = client.delete(f"/projects/{project_id}")

        assert response.status_code == 204


def test_delete_project_not_found() -> None:
    with TestClient(app) as client:
        response = client.delete(f"/projects/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}


def test_delete_project_has_tasks_returns_409() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        create_task_via_api(client, project_id)

        response = client.delete(f"/projects/{project_id}")

        assert response.status_code == 409
        assert response.json() == {"detail": "Project has tasks"}


def test_create_project_and_delete_project_and_get_project_by_id_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")
        response = client.get(f"/projects/{project_id}")
        assert response.status_code == 404


def test_double_delete_project_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")
        response = client.delete(f"/projects/{project_id}")
        assert response.status_code == 404


def test_update_after_delete_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)

        client.delete(f"/projects/{project_id}")
        response = client.patch(
            f"/projects/{project_id}",
            json={"name": "Updated Project", "description": "Updated Description"},
        )
        assert response.status_code == 404


def test_create_task_in_deleted_project_returns_404() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")
        response = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": str(project_id),
            },
        )
        assert response.status_code == 404


def test_delete_project_and_project_is_not_in_list_projects() -> None:
    with TestClient(app) as client:
        project_id_1 = create_project_via_api(client)
        create_project_via_api(client)
        client.delete(f"/projects/{project_id_1}")
        response = client.get("/projects")
        assert project_id_1 not in [project["id"] for project in response.json()]


def test_restore_project_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")
        response = client.post(f"/projects/{project_id}/restore")
        assert response.status_code == 200
        project = client.get(f"/projects/{project_id}")
        assert project.status_code == 200


def test_restore_project_not_found_returns_404() -> None:
    with TestClient(app) as client:
        response = client.post(f"/projects/{uuid4()}/restore")
        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}


def test_restore_project_after_delete_and_project_is_in_list_projects() -> None:
    with TestClient(app) as client:
        project_id_1 = create_project_via_api(client)
        create_project_via_api(client)
        response = client.get("/projects")
        assert len(response.json()) == 2

        client.delete(f"/projects/{project_id_1}")
        response = client.get("/projects")
        assert project_id_1 not in [project["id"] for project in response.json()]
        response = client.post(f"/projects/{project_id_1}/restore")
        assert response.status_code == 200
        response = client.get("/projects")
        assert len(response.json()) == 2
        assert project_id_1 in [project["id"] for project in response.json()]


def test_restore_project_and_create_task_returns_201() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        client.delete(f"/projects/{project_id}")
        response = client.get(f"/projects/{project_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}

        response = client.post(f"/projects/{project_id}/restore")
        assert response.status_code == 200

        response = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": str(project_id),
            },
        )
        assert response.status_code == 201


def test_restore_project_and_restore_task_returns_200() -> None:
    with TestClient(app) as client:
        project_id = create_project_via_api(client)
        task_id_1 = create_task_via_api(client, project_id)
        task_id_2 = create_task_via_api(client, project_id)
        client.delete(f"/tasks/{task_id_1}")
        client.delete(f"/tasks/{task_id_2}")
        response = client.delete(f"/projects/{project_id}")
        assert response.status_code == 204

        response = client.post(f"/projects/{project_id}/restore")
        assert response.status_code == 200

        response = client.get(
            "/tasks", params={"project_id": str(project_id), "limit": 10, "offset": 0}
        )
        assert len(response.json()) == 2
