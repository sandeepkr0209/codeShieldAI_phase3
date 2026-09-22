"""
Authentication routes: email+password and Google OAuth 2.0.

Tokens are issued as secure HttpOnly cookies (access_token,
refresh_token) rather than being handed to client-side JS, per the
project's security requirements. The frontend never reads or stores
these tokens directly — the browser sends them automatically on
same-site requests (see frontend/src/services/api.ts's
`credentials: "include"`).
"""
import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token, InvalidTokenError
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, UserLogin, UserRead, UserRegister
from app.services.auth import service as auth_service
from app.services.auth.google_oauth import (
    GoogleOAuthError,
    GoogleOAuthNotConfigured,
    build_authorization_url,
    exchange_code_for_userinfo,
    generate_state,
    is_configured as google_is_configured,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
OAUTH_STATE_COOKIE = "oauth_state"


def _set_auth_cookies(response: Response, user: User) -> None:
    settings = get_settings()
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        ACCESS_COOKIE, access_token,
        httponly=True, secure=settings.COOKIE_SECURE, samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE, refresh_token,
        httponly=True, secure=settings.COOKIE_SECURE, samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)) -> UserRead:
    if auth_service.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    user = auth_service.register_user(db, name=payload.name, email=payload.email, password=payload.password)
    auth_service.record_login(db, user)
    _set_auth_cookies(response, user)
    return UserRead.model_validate(user)


@router.post("/login", response_model=UserRead)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)) -> UserRead:
    user = auth_service.authenticate_user(db, email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    auth_service.record_login(db, user)
    _set_auth_cookies(response, user)
    return UserRead.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    _clear_auth_cookies(response)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/refresh", response_model=UserRead)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
) -> UserRead:
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")

    try:
        user_id = decode_token(refresh_token, expected_type="refresh")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = auth_service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    _set_auth_cookies(response, user)  # rotates both tokens
    return UserRead.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if current_user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account signed in with Google and has no password to change",
        )
    ok = auth_service.change_password(
        db, current_user, current_password=payload.current_password, new_password=payload.new_password
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")


# --- Google OAuth ---------------------------------------------------

@router.get("/google")
def google_login(response: Response) -> RedirectResponse:
    if not google_is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Google sign-in is not configured on this server. Set GOOGLE_CLIENT_ID and "
                "GOOGLE_CLIENT_SECRET in backend/.env (see README for how to obtain them)."
            ),
        )
    state = generate_state()
    redirect = RedirectResponse(url=build_authorization_url(state))
    settings = get_settings()
    redirect.set_cookie(
        OAUTH_STATE_COOKIE, state, httponly=True, secure=settings.COOKIE_SECURE,
        samesite="lax", max_age=600, path="/",
    )
    return redirect


@router.get("/google/callback")
def google_callback(
    code: str | None = None,
    state: str | None = None,
    oauth_state: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()

    if not code or not state or state != oauth_state:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=oauth_state_mismatch")

    try:
        profile = exchange_code_for_userinfo(code)
    except (GoogleOAuthNotConfigured, GoogleOAuthError) as exc:
        logger.error("Google OAuth callback failed: %s", exc)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=oauth_failed")

    google_id = profile.get("sub")
    email = profile.get("email")
    if not google_id or not email:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=oauth_incomplete_profile")

    user = auth_service.get_or_create_google_user(
        db,
        google_id=google_id,
        email=email,
        name=profile.get("name") or email.split("@")[0],
        profile_image=profile.get("picture"),
    )
    auth_service.record_login(db, user)

    redirect = RedirectResponse(url=f"{settings.FRONTEND_URL}/")
    redirect.delete_cookie(OAUTH_STATE_COOKIE, path="/")
    _set_auth_cookies(redirect, user)
    return redirect
