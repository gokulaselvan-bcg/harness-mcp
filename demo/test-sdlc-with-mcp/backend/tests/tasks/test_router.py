from fastapi.testclient import TestClient


def test_post_creates_task_returns_201(client: TestClient) -> None:
    response = client.post(
        "/v1/tasks",
        json={"title": "Buy milk", "description": "2L"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["description"] == "2L"
    assert body["completed"] is False
    assert isinstance(body["id"], int)


def test_post_task_rejects_empty_title(client: TestClient) -> None:
    response = client.post("/v1/tasks", json={"title": ""})

    assert response.status_code == 422


def test_post_task_rejects_missing_title(client: TestClient) -> None:
    response = client.post("/v1/tasks", json={})

    assert response.status_code == 422


def test_get_tasks_returns_list(client: TestClient) -> None:
    client.post("/v1/tasks", json={"title": "a"})
    client.post("/v1/tasks", json={"title": "b"})

    response = client.get("/v1/tasks")

    assert response.status_code == 200
    body = response.json()
    assert [t["title"] for t in body["tasks"]] == ["a", "b"]


def test_get_tasks_empty_returns_empty_list(client: TestClient) -> None:
    response = client.get("/v1/tasks")

    assert response.status_code == 200
    assert response.json() == {"tasks": []}


def test_put_task_updates_fields(client: TestClient) -> None:
    created = client.post("/v1/tasks", json={"title": "old"}).json()

    response = client.put(
        f"/v1/tasks/{created['id']}",
        json={"title": "new", "completed": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "new"
    assert body["completed"] is True


def test_put_task_missing_returns_404(client: TestClient) -> None:
    response = client.put("/v1/tasks/999", json={"title": "x"})

    assert response.status_code == 404


def test_delete_task_returns_204(client: TestClient) -> None:
    created = client.post("/v1/tasks", json={"title": "x"}).json()

    response = client.delete(f"/v1/tasks/{created['id']}")

    assert response.status_code == 204

    listed = client.get("/v1/tasks").json()
    assert listed == {"tasks": []}


def test_delete_task_missing_returns_404(client: TestClient) -> None:
    response = client.delete("/v1/tasks/999")

    assert response.status_code == 404
