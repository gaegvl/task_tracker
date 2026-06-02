from fastapi.testclient import TestClient
from src.main import app
from uuid import uuid4


def test_create_project() -> None:
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

        task = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": response.json()["id"],
            },
        )
        assert task.status_code == 201
        assert task.json()["id"] is not None
        assert task.json()["title"] == "Test Task"


def test_get_project_by_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = response.json()["id"]

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


def test_get_list_projects() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = response.json()["id"]
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


def test_update_project() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = response.json()["id"]
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


def test_delete_project() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = response.json()["id"]
        response = client.delete(f"/projects/{project_id}")
        assert response.status_code == 204


def test_delete_project_not_found() -> None:
    with TestClient(app) as client:
        response = client.delete(f"/projects/{uuid4()}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}


def test_delete_project_has_tasks() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test Description"},
        )
        project_id = response.json()["id"]
        client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "project_id": project_id,
            },
        )

        response = client.delete(f"/projects/{project_id}")
        assert response.status_code == 409
        assert response.json() == {"detail": "Project has tasks"}
