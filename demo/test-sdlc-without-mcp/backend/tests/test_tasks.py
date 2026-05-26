def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Write tests", "description": "pytest suite"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Write tests"
    assert data["description"] == "pytest suite"
    assert data["completed"] is False
    assert "created_at" in data


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_read_task(client):
    created = client.post("/tasks", json={"title": "Read me"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Read me"


def test_read_task_not_found(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_list_tasks(client):
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B"})
    response = client.get("/tasks")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["A", "B"]


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Old"}).json()
    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "New", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New"
    assert data["completed"] is True


def test_update_task_partial(client):
    created = client.post(
        "/tasks", json={"title": "Keep", "description": "orig"}
    ).json()
    response = client.put(
        f"/tasks/{created['id']}", json={"completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Keep"
    assert data["description"] == "orig"
    assert data["completed"] is True


def test_update_task_not_found(client):
    response = client.put("/tasks/9999", json={"title": "x"})
    assert response.status_code == 404


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
