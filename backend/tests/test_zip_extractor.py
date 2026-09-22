import zipfile
from pathlib import Path

import pytest

from app.services.code_analysis.zip_extractor import (
    UnsafeArchiveError,
    extract_zip_safely,
    sha256_of_file,
)


def _make_zip(tmp_path: Path, entries: dict[str, bytes]) -> Path:
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return zip_path


def test_extracts_normal_files(tmp_path):
    zip_path = _make_zip(tmp_path, {"app.py": b"print('hi')", "utils/helpers.py": b"def f(): pass"})
    dest = tmp_path / "out"
    extracted = extract_zip_safely(zip_path, dest)
    assert len(extracted) == 2
    assert (dest / "app.py").read_bytes() == b"print('hi')"
    assert (dest / "utils" / "helpers.py").exists()


def test_ignores_node_modules_and_git(tmp_path):
    zip_path = _make_zip(
        tmp_path,
        {
            "app.py": b"code",
            "node_modules/pkg/index.js": b"junk",
            ".git/HEAD": b"ref: refs/heads/main",
        },
    )
    dest = tmp_path / "out"
    extracted = extract_zip_safely(zip_path, dest)
    extracted_names = {p.name for p in extracted}
    assert "app.py" in extracted_names
    assert not (dest / "node_modules").exists()
    assert not (dest / ".git").exists()


def test_rejects_path_traversal(tmp_path):
    zip_path = tmp_path / "evil.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../../etc/passwd", b"malicious")
    dest = tmp_path / "out"
    with pytest.raises(UnsafeArchiveError):
        extract_zip_safely(zip_path, dest)


def test_sha256_is_deterministic(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"hello world")
    assert sha256_of_file(f) == sha256_of_file(f)
    assert len(sha256_of_file(f)) == 64
