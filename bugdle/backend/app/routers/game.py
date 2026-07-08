from fastapi import APIRouter, Request

from app.limiter import limiter
from app.schemas.game import GuessRequest, GuessResponse, TodayPuzzleResponse
from app.services import game_service

router = APIRouter(prefix="/api/game", tags=["game"])


@router.get("/today", response_model=TodayPuzzleResponse)
@limiter.limit("30/minute")
def today(request: Request):
    # No auth required: anonymous play is first-class.
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        scenario = game_service.get_today_scenario(db)
        return game_service.start_attempt(db, scenario)
    finally:
        db.close()


@router.post("/guess", response_model=GuessResponse, response_model_exclude_none=True)
@limiter.limit("10/minute")
def guess(request: Request, payload: GuessRequest):
    # No auth required. Rate-limited more strictly because this endpoint is
    # the one someone would script to brute-force answers.
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        response, _new_token = game_service.submit_guess(
            db, payload.attempt_token, payload.answer
        )
        return response
    finally:
        db.close()
