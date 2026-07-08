from pydantic import BaseModel


class ClueOut(BaseModel):
    order: int
    text: str


class TodayPuzzleResponse(BaseModel):
    attempt_token: str
    scenario_category: str
    clues: list[ClueOut]
    guesses_remaining: int
    answer_options: list[str]
    game_over: bool


class GuessRequest(BaseModel):
    attempt_token: str
    answer: str


class GuessResponse(BaseModel):
    # Freshly re-issued signed token reflecting the new game state; the client
    # must replace its token with this after every guess.
    attempt_token: str
    correct: bool
    game_over: bool
    guesses_remaining: int
    next_clue: ClueOut | None = None
    # MUST only be populated when game_over is true (secret-leak invariant).
    correct_answer: str | None = None
