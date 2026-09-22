"""
GitHub repository ingestion for PUBLIC repositories only — no
authentication is required or used. Downloads the repo's default
branch as a zip archive via GitHub's codeload endpoint and reuses the
same safe ZIP extractor as manual uploads (path traversal protection,
size limits, etc. all still apply).
"""
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.services.code_analysis.zip_extractor import UnsafeArchiveError, extract_zip_safely

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
CODELOAD_BASE = "https://codeload.github.com"
DOWNLOAD_TIMEOUT_SECONDS = 60
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024


class GitHubIngestionError(Exception):
    pass


def parse_owner_repo(repo_url: str) -> tuple[str, str]:
    """Extracts (owner, repo) from a GitHub URL like
    https://github.com/owner/repo or https://github.com/owner/repo.git"""
    parsed = urlparse(repo_url.strip())
    parts = [p for p in parsed.path.split("/") if p]
    if parsed.netloc not in ("github.com", "www.github.com") or len(parts) < 2:
        raise GitHubIngestionError(f"Not a valid GitHub repository URL: {repo_url}")
    owner, repo = parts[0], re.sub(r"\.git$", "", parts[1])
    return owner, repo


def _get_default_branch(owner: str, repo: str) -> str:
    with httpx.Client(timeout=15) as client:
        resp = client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")
    if resp.status_code == 404:
        raise GitHubIngestionError(f"Repository not found or is private: {owner}/{repo}")
    resp.raise_for_status()
    return resp.json().get("default_branch", "main")


def download_and_extract_repo(repo_url: str, dest_dir: Path) -> list[Path]:
    """
    Downloads the given public GitHub repository's default branch and
    extracts it safely into `dest_dir`. Returns the list of extracted
    file paths.
    """
    owner, repo = parse_owner_repo(repo_url)
    branch = _get_default_branch(owner, repo)

    zip_url = f"{CODELOAD_BASE}/{owner}/{repo}/zip/refs/heads/{branch}"
    tmp_zip_path = dest_dir.parent / f"{repo}-{branch}.zip"
    dest_dir.parent.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    with httpx.stream("GET", zip_url, timeout=DOWNLOAD_TIMEOUT_SECONDS, follow_redirects=True) as resp:
        if resp.status_code != 200:
            raise GitHubIngestionError(f"Failed to download repository archive (HTTP {resp.status_code})")
        with open(tmp_zip_path, "wb") as f:
            for chunk in resp.iter_bytes():
                downloaded += len(chunk)
                if downloaded > MAX_DOWNLOAD_BYTES:
                    raise GitHubIngestionError("Repository archive exceeds the allowed download size")
                f.write(chunk)

    try:
        extracted = extract_zip_safely(tmp_zip_path, dest_dir)
    except UnsafeArchiveError as exc:
        raise GitHubIngestionError(str(exc)) from exc
    finally:
        tmp_zip_path.unlink(missing_ok=True)

    return extracted
