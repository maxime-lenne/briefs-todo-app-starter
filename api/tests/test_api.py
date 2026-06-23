"""Integration-style tests against the FastAPI app via TestClient."""


def test_list_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client):
    response = client.post(
        "/todos",
        json={"title": "Write tests", "description": "with pytest"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == "Write tests"
    assert body["description"] == "with pytest"
    assert body["completed"] is False
    assert "created_at" in body


def test_create_todo_validation_error(client):
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 422


def test_get_todo(client):
    created = client.post("/todos", json={"title": "Read book"}).json()

    response = client.get(f"/todos/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Read book"


def test_get_todo_not_found(client):
    response = client.get("/todos/9999")
    assert response.status_code == 404


def test_update_todo(client):
    created = client.post("/todos", json={"title": "Old title"}).json()

    response = client.put(
        f"/todos/{created['id']}",
        json={"title": "New title", "completed": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New title"
    assert body["completed"] is True


def test_update_todo_not_found(client):
    response = client.put("/todos/9999", json={"title": "nope"})
    assert response.status_code == 404


def test_delete_todo(client):
    created = client.post("/todos", json={"title": "Delete me"}).json()

    response = client.delete(f"/todos/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/todos/{created['id']}").status_code == 404


def test_delete_todo_not_found(client):
    response = client.delete("/todos/9999")
    assert response.status_code == 404
