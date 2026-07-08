from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User


def register(db: Session, data) -> User:
    # Check email and username uniqueness SEPARATELY so the error can say which
    # one collided (intentional, unlike login which must stay generic).
    if db.query(User).filter(User.email == data.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    if db.query(User).filter(User.username == data.username).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, credentials) -> User:
    user = db.query(User).filter(User.email == credentials.email).first()
    # Generic failure for BOTH "not found" and "wrong password" to prevent
    # account enumeration.
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    access = create_access_token(user.id, user.username, user.email)
    refresh = create_refresh_token(user.id)
    return access, refresh
