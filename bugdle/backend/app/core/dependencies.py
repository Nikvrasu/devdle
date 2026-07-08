from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    payload = decode_token(creds.credentials, expected_type="access")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user


def get_current_user_optional(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User | None:
    # Used by the game endpoints: logged-in users get their attempt recorded,
    # anonymous users continue exactly as before (return None).
    if creds is None:
        return None
    try:
        payload = decode_token(creds.credentials, expected_type="access")
    except HTTPException:
        return None
    return db.query(User).filter(User.id == int(payload["sub"])).first()
