"""
Auth service — business logic for user registration/authentication,
kept separate from the API route handlers.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import AuthProvider, User


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email.lower())
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def register_user(db: Session, *, name: str, email: str, password: str) -> User:
    user = User(
        name=name,
        email=email.lower(),
        password_hash=hash_password(password),
        auth_provider=AuthProvider.PASSWORD,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or user.password_hash is None:
        return None  # either no such user, or a Google-only account with no password
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_or_create_google_user(db: Session, *, google_id: str, email: str, name: str, profile_image: str | None) -> User:
    stmt = select(User).where(User.google_id == google_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is not None:
        return user

    # A password account with this email may already exist — link the
    # Google identity to it rather than creating a duplicate account.
    existing = get_user_by_email(db, email)
    if existing is not None:
        existing.google_id = google_id
        if not existing.profile_image:
            existing.profile_image = profile_image
        db.commit()
        db.refresh(existing)
        return existing

    user = User(
        name=name,
        email=email.lower(),
        password_hash=None,
        auth_provider=AuthProvider.GOOGLE,
        google_id=google_id,
        profile_image=profile_image,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def record_login(db: Session, user: User) -> None:
    user.last_login = datetime.now(timezone.utc)
    db.commit()


def change_password(db: Session, user: User, *, current_password: str, new_password: str) -> bool:
    if user.password_hash is None or not verify_password(current_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    db.commit()
    return True
