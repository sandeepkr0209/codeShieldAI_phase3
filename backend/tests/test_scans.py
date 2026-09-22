def _create_project(client):
    payload = {
        "name": "Demo Project",
        "target_type": "github",
        "target_value": "https://github.com/example/demo",
    }
    response = client.post("/api/projects", json=payload)
    return response.json()


def test_create_scan(client):
    project = _create_project(client)
    response = client.post(
        f"/api/projects/{project['id']}/scans",
        json={"scan_type": "source_code"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["project_id"] == project["id"]


def test_list_scans_for_project(client):
    project = _create_project(client)
    client.post(f"/api/projects/{project['id']}/scans", json={"scan_type": "source_code"})
    response = client.get(f"/api/projects/{project['id']}/scans")
    assert response.status_code == 200
    assert len(response.json()) == 1
