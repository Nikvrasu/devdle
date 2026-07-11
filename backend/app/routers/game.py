from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_current_user_optional
from app.database import get_db
from app.limiter import limiter
from app.schemas.game import GuessRequest, GuessResponse, TodayPuzzleResponse
from app.services import game_service

router = APIRouter(prefix="/api/game", tags=["game"])


@router.get("/today", response_model=TodayPuzzleResponse)
@limiter.limit("30/minute")
def today(
    request: Request,
    db=Depends(get_db),
    user=Depends(get_current_user_optional),
):
    # No auth required: anonymous play is first-class. Logged-in users get
    # their attempt recorded against their account.
    scenario = game_service.get_today_scenario(db)
    return game_service.start_attempt(db, scenario, user=user)


@router.post("/guess", response_model=GuessResponse, response_model_exclude_none=True)
@limiter.limit("10/minute")
def guess(
    request: Request,
    payload: GuessRequest,
    db=Depends(get_db),
    user=Depends(get_current_user_optional),
):
    # No auth required. Rate-limited more strictly because this endpoint is
    # the one someone would script to brute-force answers.
    response, _new_token = game_service.submit_guess(
        db, payload.attempt_token, payload.answer, user=user
    )
    return response
