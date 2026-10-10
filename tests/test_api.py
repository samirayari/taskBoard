import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def empty_store():
    """Every test starts with an empty storage."""
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client():
    return TestClient(app)


def create_task(client, title="Learn Git"):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == 201
    return response.json()


# --- System ------------------------------------------------------------------


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"name": "TaskBoard", "version": "1.0.0"}


# --- Read and create ---------------------------------------------------------


def test_list_is_empty_at_start(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_task(client):
    created = create_task(client, "  Write the tests  ")
    assert created == {"id": 1, "title": "Write the tests", "completed": False}

    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json() == created

    response = client.get("/tasks")
    assert response.json() == [created]


def test_ids_are_incremented(client):
    first = create_task(client, "First")
    second = create_task(client, "Second")
    assert (first["id"], second["id"]) == (1, 2)


# --- Update ------------------------------------------------------------------


def test_update_title(client):
    create_task(client)
    response = client.patch("/tasks/1", json={"title": "Learn Docker"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Learn Docker", "completed": False}


def test_update_completed(client):
    create_task(client)
    response = client.patch("/tasks/1", json={"completed": True})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Learn Git", "completed": True}

    assert client.get("/tasks/1").json()["completed"] is True


def test_update_without_fields_is_rejected(client):
    create_task(client)
    response = client.patch("/tasks/1", json={})
    assert response.status_code == 422


# --- Delete ------------------------------------------------------------------


def test_delete_task(client):
    create_task(client)
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""

    assert client.get("/tasks/1").status_code == 404
    assert client.get("/tasks").json() == []


# --- Unknown id --------------------------------------------------------------


def test_get_unknown_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task 999 not found"}


def test_update_unknown_task_returns_404(client):
    response = client.patch("/tasks/999", json={"completed": True})
    assert response.status_code == 404


def test_delete_unknown_task_returns_404(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404


# --- Title validation --------------------------------------------------------


@pytest.mark.parametrize("title", ["", "   ", "a" * 101])
def test_create_rejects_invalid_title(client, title):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == 422
    assert client.get("/tasks").json() == []


def test_create_accepts_100_characters_title(client):
    created = create_task(client, "a" * 100)
    assert len(created["title"]) == 100


@pytest.mark.parametrize("title", ["", "   ", "a" * 101])
def test_update_rejects_invalid_title(client, title):
    create_task(client)
    response = client.patch("/tasks/1", json={"title": title})
    assert response.status_code == 422
    assert client.get("/tasks/1").json()["title"] == "Learn Git"
