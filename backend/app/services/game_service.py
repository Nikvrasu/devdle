import json
import os
import random

from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.attempt import Attempt
from app.models.clue import Clue
from app.models.scenario import Scenario
from app.schemas.game import ClueOut, GuessResponse, TodayPuzzleResponse


# ---------------------------------------------------------------------------
# CRITICAL SECURITY INVARIANT
# The canonical answer and any UNREVEALED clue must NEVER appear in an API
# response body until the game is over (solved, or all 5 guesses used). A
# violation is a security bug, not a game bug. Enforce it here in the service
# layer: only `next_clue` (the single newly revealed clue) is ever returned
# mid-game, and `correct_answer` is only attached once `game_over` is true.
# ---------------------------------------------------------------------------

ALGORITHM = "HS256"
SECRET = settings.JWT_SECRET
_MAX_GUESSES = 5

_SEED_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "seeds", "scenarios.json"
)

with open(_SEED_FILE, "r", encoding="utf-8") as _f:
    _SEED_DATA = json.load(_f)
_ANSWER_POOL = _SEED_DATA.get("answer_pool", [])


def _create_token(scenario_id: int, guesses_used: int, clues_revealed: int, solved: bool) -> str:
    payload = {
        "scenario_id": scenario_id,
        "guesses_used": guesses_used,
        "clues_revealed": clues_revealed,
        "solved": solved,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    # Raises JWTError if the signature is invalid or the token is malformed.
    # The server trusts ONLY the decoded claims, never client-supplied state,
    # so a client cannot forge "I've only used 1 guess".
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])


def get_today_scenario(db: Session) -> Scenario:
    from datetime import date

    scenario = (
        db.query(Scenario).filter(Scenario.active_date == date.today()).first()
    )
    if scenario is None:
        raise HTTPException(
            status_code=404,
            detail="No puzzle is available for today.",
        )
    return scenario


def start_attempt(db: Session, scenario: Scenario, user=None) -> TodayPuzzleResponse:
    token = _create_token(scenario.id, guesses_used=0, clues_revealed=1, solved=False)

    clues = (
        db.query(Clue)
        .filter(Clue.scenario_id == scenario.id)
        .order_by(Clue.order)
        .limit(1)
        .all()
    )

    answer_options = list(_ANSWER_POOL)
    random.shuffle(answer_options)

    if user is not None:
        # Phase 3 wires logged-in users here; Phase 2 always passes None.
        _persist_attempt(db, user, scenario, guesses_used=0, solved=False, clues_revealed=1)

    return TodayPuzzleResponse(
        attempt_token=token,
        scenario_category=scenario.category,
        clues=[ClueOut(order=c.order, text=c.text) for c in clues],
        guesses_remaining=_MAX_GUESSES,
        answer_options=answer_options,
        game_over=False,
    )


def submit_guess(db: Session, token: str, answer: str, user=None) -> tuple[GuessResponse, str]:
    try:
        claims = _decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or tampered attempt token.",
        )

    scenario_id = claims["scenario_id"]
    guesses_used = claims["guesses_used"]
    clues_revealed = claims["clues_revealed"]
    solved = claims["solved"]

    # Reject further guesses once the game is over, even if the client bypasses
    # the UI and resubmits the (now-expired) token.
    if solved or guesses_used >= _MAX_GUESSES:
        raise HTTPException(
            status_code=400,
            detail="This game is already over; no further guesses are accepted.",
        )

    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found.")

    correct = answer.strip().casefold() == scenario.answer.strip().casefold()
    guesses_used += 1

    if correct:
        solved = True
        game_over = True
        next_clue = None
        correct_answer = scenario.answer  # allowed: game is over
    elif guesses_used >= _MAX_GUESSES:
        # Loss: all guesses exhausted. Reveal the answer now that game is over.
        game_over = True
        solved = False
        next_clue = None
        correct_answer = scenario.answer  # allowed: game is over
    else:
        # Wrong but guesses remain: reveal exactly one new clue, no answer.
        game_over = False
        solved = False
        clues_revealed += 1
        next_clue = (
            db.query(Clue)
            .filter(Clue.scenario_id == scenario_id, Clue.order == clues_revealed)
            .first()
        )
        correct_answer = None  # SECRET-LEAK INVARIANT: must stay absent

    new_token = _create_token(scenario_id, guesses_used, clues_revealed, solved)

    if user is not None:
        _persist_attempt(db, user, scenario, guesses_used, solved, clues_revealed)

    response = GuessResponse(
        attempt_token=new_token,
        correct=correct,
        game_over=game_over,
        guesses_remaining=_MAX_GUESSES - guesses_used,
        next_clue=ClueOut(order=next_clue.order, text=next_clue.text) if next_clue else None,
        correct_answer=correct_answer,
    )
    return response, new_token


def _persist_attempt(
    db: Session, user, scenario: Scenario, guesses_used: int, solved: bool, clues_revealed: int
) -> None:
    # Used once logged-in users exist (Phase 3). For anonymous play in Phase 2
    # no Attempt row is written — the signed token is the source of truth.
    attempt = (
        db.query(Attempt)
        .filter(Attempt.user_id == user.id, Attempt.scenario_id == scenario.id)
        .first()
    )
    if attempt is None:
        attempt = Attempt(user_id=user.id, scenario_id=scenario.id)
        db.add(attempt)
    attempt.guesses_used = guesses_used
    attempt.solved = solved
    attempt.clues_revealed = clues_revealed
    db.commit()
