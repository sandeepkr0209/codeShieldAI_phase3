def test_create_project(client):
    payload = {
        "name": "Demo Vulnerable App",
        "description": "A test project",
        "target_type": "website",
        "target_value": "http://localhost:3000",
    }
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["target_type"] == "website"
    assert "id" in body


def test_list_projects_empty(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_get_project_not_found(client):
    import uuid

    response = client.get(f"/api/projects/{uuid.uuid4()}")
    assert response.status_code == 404


def test_create_project_validation_error(client):
    # Missing required "name"
    payload = {"target_type": "zip", "target_value": "source.zip"}
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 422
