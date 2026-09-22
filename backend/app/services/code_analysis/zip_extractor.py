"""
Safe ZIP extraction.

Prevents path traversal ("zip slip"), oversized files, oversized
archives, and dangerous archive structures. This is the only place
in the codebase that extracts user-supplied ZIP files.
"""
import hashlib
import os
import zipfile
from pathlib import Path

MAX_ARCHIVE_BYTES = 100 * 1024 * 1024  # 100 MB total uncompressed
MAX_SINGLE_FILE_BYTES = 15 * 1024 * 1024  # 15 MB per file
MAX_FILE_COUNT = 5000

IGNORED_DIR_NAMES = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", ".idea", ".vscode", "target", "vendor",
}


class UnsafeArchiveError(Exception):
    pass


def _is_within_directory(directory: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def extract_zip_safely(zip_path: Path, dest_dir: Path) -> list[Path]:
    """
    Extracts `zip_path` into `dest_dir`, enforcing size/count limits and
    rejecting any entry that would escape `dest_dir`. Returns the list of
    extracted file paths (ignored directories excluded).
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []

    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        if len(infos) > MAX_FILE_COUNT:
            raise UnsafeArchiveError(f"Archive contains too many entries (> {MAX_FILE_COUNT})")

        total_size = sum(i.file_size for i in infos)
        if total_size > MAX_ARCHIVE_BYTES:
            raise UnsafeArchiveError("Archive uncompressed size exceeds the allowed limit")

        for info in infos:
            if info.is_dir():
                continue
            if info.file_size > MAX_SINGLE_FILE_BYTES:
                continue  # skip oversized individual files rather than failing the whole upload

            # Reject absolute paths and any ".." component (zip slip protection)
            normalized = os.path.normpath(info.filename)
            if normalized.startswith("..") or os.path.isabs(normalized):
                raise UnsafeArchiveError(f"Unsafe path in archive: {info.filename}")

            parts = Path(normalized).parts
            if any(p in IGNORED_DIR_NAMES for p in parts):
                continue

            target_path = dest_dir / normalized
            if not _is_within_directory(dest_dir, target_path):
                raise UnsafeArchiveError(f"Path traversal attempt detected: {info.filename}")

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, open(target_path, "wb") as target:
                target.write(source.read())
            extracted.append(target_path)

    return extracted


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
