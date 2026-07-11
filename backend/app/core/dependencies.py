from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def _resolve_user(request: Request, creds: HTTPAuthorizationCredentials | None, db: Session, required: bool) -> User | None:
    # 1) Access token from the Authorization header (normal case).
    if creds and creds.credentials:
        try:
            payload = decode_token(creds.credentials, expected_type="access")
            user = db.query(User).filter(User.id == int(payload["sub"])).first()
            if user is not None:
                return user
            if required:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
            return None
        except HTTPException:
            # Access token expired/invalid — fall through to the refresh cookie.
            pass

    # 2) Refresh cookie. This keeps a logged-in user attributed even if their
    # short-lived access token expired mid-game (e.g. while reading clues).
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user = db.query(User).filter(User.id == int(payload["sub"])).first()
            if user is not None:
                return user
        except HTTPException:
            pass

    if required:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    user = _resolve_user(request, creds, db, required=True)
    assert user is not None
    return user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User | None:
    # Used by the game endpoints: logged-in users get their attempt recorded,
    # anonymous users continue exactly as before (return None).
    return _resolve_user(request, creds, db, required=False)
