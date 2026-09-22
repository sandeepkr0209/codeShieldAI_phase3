"""
Minimal Google OAuth 2.0 (Authorization Code flow) helper.

Deliberately implemented by hand against Google's documented endpoints
(no extra SDK dependency) so the flow is easy to read and explain.
Requires GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REDIRECT_URI
to be set — obtained from the Google Cloud Console (APIs & Services >
Credentials > OAuth 2.0 Client ID). Without them, /api/auth/google
returns 503 rather than silently failing.
"""
import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = "openid email profile"


class GoogleOAuthNotConfigured(Exception):
    pass


class GoogleOAuthError(Exception):
    pass


def is_configured() -> bool:
    settings = get_settings()
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def generate_state() -> str:
    """CSRF-protection token for the OAuth redirect — caller stores this
    in a short-lived cookie and verifies it on callback."""
    return secrets.token_urlsafe(24)


def build_authorization_url(state: str) -> str:
    settings = get_settings()
    if not is_configured():
        raise GoogleOAuthNotConfigured("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET are not set in .env")

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"


def exchange_code_for_userinfo(code: str) -> dict:
    """Exchanges an authorization code for tokens, then fetches the
    user's Google profile. Returns {sub, email, name, picture}."""
    settings = get_settings()
    if not is_configured():
        raise GoogleOAuthNotConfigured("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET are not set in .env")

    with httpx.Client(timeout=15) as client:
        token_response = client.post(
            TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code != 200:
            raise GoogleOAuthError(f"Token exchange failed: {token_response.text[:300]}")

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise GoogleOAuthError("Google did not return an access token")

        userinfo_response = client.get(
            USERINFO_ENDPOINT, headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_response.status_code != 200:
            raise GoogleOAuthError(f"Failed to fetch Google profile: {userinfo_response.text[:300]}")

        return userinfo_response.json()
