import pytest

from app.services.web_analysis.scope import ScanScope, ScopeValidationError, validate_target


def test_validate_target_accepts_http_url():
    scope = validate_target("http://example.com/app")
    assert "example.com" in scope.allowed_hosts


def test_validate_target_rejects_non_http_scheme():
    with pytest.raises(ScopeValidationError):
        validate_target("ftp://example.com")


def test_validate_target_rejects_missing_hostname():
    with pytest.raises(ScopeValidationError):
        validate_target("http://")


def test_scope_is_url_in_scope_same_host():
    scope = ScanScope(target_url="http://example.com/")
    assert scope.is_url_in_scope("http://example.com/other-page")


def test_scope_rejects_different_host():
    scope = ScanScope(target_url="http://example.com/")
    assert not scope.is_url_in_scope("http://evil.com/")


def test_scope_rejects_non_http_scheme():
    scope = ScanScope(target_url="http://example.com/")
    assert not scope.is_url_in_scope("javascript:alert(1)")
