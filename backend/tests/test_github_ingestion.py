import pytest

from app.services.source_ingestion.github import GitHubIngestionError, parse_owner_repo


def test_parse_owner_repo_from_plain_url():
    owner, repo = parse_owner_repo("https://github.com/octocat/Hello-World")
    assert owner == "octocat"
    assert repo == "Hello-World"


def test_parse_owner_repo_strips_git_suffix():
    owner, repo = parse_owner_repo("https://github.com/octocat/Hello-World.git")
    assert repo == "Hello-World"


def test_parse_owner_repo_rejects_non_github_url():
    with pytest.raises(GitHubIngestionError):
        parse_owner_repo("https://gitlab.com/octocat/Hello-World")


def test_parse_owner_repo_rejects_malformed_url():
    with pytest.raises(GitHubIngestionError):
        parse_owner_repo("https://github.com/octocat")
