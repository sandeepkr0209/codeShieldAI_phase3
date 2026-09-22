"""
API-level tests for ZIP upload. Redirects storage to a temp directory
so tests never touch the real backend/storage/ folder.
"""
import io
import zipfile

import pytest

import app.services.scans.pipeline as pipeline_module


@pytest.fixture(autouse=True)
def _isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline_module, "STORAGE_ROOT", tmp_path / "projects")


def _make_zip_bytes(entries: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _create_project(client) -> dict:
    resp = client.post(
        "/api/projects",
        json={"name": "Upload Test", "target_type": "zip", "target_value": "source.zip"},
    )
    return resp.json()


def test_upload_zip_creates_source_files(client):
    project = _create_project(client)
    zip_bytes = _make_zip_bytes({"app.py": b"print('hi')", "utils.py": b"def f(): pass"})

    response = client.post(
        f"/api/projects/{project['id']}/source/upload",
        files={"file": ("source.zip", zip_bytes, "application/zip")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["files_ingested"] == 2
    assert body["languages"]["python"] == 2


def test_upload_rejects_non_zip_file(client):
    project = _create_project(client)
    response = client.post(
        f"/api/projects/{project['id']}/source/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_for_missing_project_returns_404(client):
    import uuid

    zip_bytes = _make_zip_bytes({"app.py": b"code"})
    response = client.post(
        f"/api/projects/{uuid.uuid4()}/source/upload",
        files={"file": ("source.zip", zip_bytes, "application/zip")},
    )
    assert response.status_code == 404


def test_list_source_files_after_upload(client):
    project = _create_project(client)
    zip_bytes = _make_zip_bytes({"main.py": b"x = 1"})
    client.post(
        f"/api/projects/{project['id']}/source/upload",
        files={"file": ("source.zip", zip_bytes, "application/zip")},
    )

    response = client.get(f"/api/projects/{project['id']}/source-files")
    assert response.status_code == 200
    files = response.json()
    assert len(files) == 1
    assert files[0]["path"] == "main.py"
    assert files[0]["language"] == "python"
