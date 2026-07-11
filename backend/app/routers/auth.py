from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.database import get_db
from app.limiter import limiter
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

# refresh cookie lifetime in seconds (14 days)
_REFRESH_MAX_AGE = 14 * 24 * 3600


def _set_refresh_cookie(response: Response, refresh_token: str, request: Request) -> None:
    # Refresh token lives ONLY in an httpOnly cookie — never in the JSON body.
    # `secure` is enabled on HTTPS; over plain HTTP (local dev) it is omitted so
    # the cookie is still usable.
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        max_age=_REFRESH_MAX_AGE,
    )


@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
def register(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = auth_service.register(db, payload)
    access, refresh = auth_service.issue_tokens(user)
    _set_refresh_cookie(response, refresh, request)
    return TokenResponse(access_token=access)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate(db, payload)
    access, refresh = auth_service.issue_tokens(user)
    _set_refresh_cookie(response, refresh, request)
    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        # Clean 401 (not a server error) when no cookie is present.
        raise HTTPException(status_code=401, detail="No refresh token.")
    payload = decode_token(token, expected_type="refresh")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    # Rotate the refresh token on every refresh (safer than reusing it).
    access, refresh = auth_service.issue_tokens(user)
    _set_refresh_cookie(response, refresh, request)
    return TokenResponse(access_token=access)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"status": "ok"}
