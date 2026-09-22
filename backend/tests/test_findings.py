def test_get_findings_empty_for_new_scan(client):
    project_resp = client.post(
        "/api/projects",
        json={
            "name": "Demo",
            "target_type": "zip",
            "target_value": "demo.zip",
        },
    )
    project = project_resp.json()
    scan_resp = client.post(
        f"/api/projects/{project['id']}/scans",
        json={"scan_type": "source_code"},
    )
    scan = scan_resp.json()

    response = client.get(f"/api/scans/{scan['id']}/findings")
    assert response.status_code == 200
    assert response.json() == []


def test_get_finding_not_found(client):
    import uuid

    response = client.get(f"/api/findings/{uuid.uuid4()}")
    assert response.status_code == 404
