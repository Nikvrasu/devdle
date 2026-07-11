from datetime import date
from typing import Dict

from pydantic import BaseModel


class StatsResponse(BaseModel):
    games_played: int
    win_rate: float
    current_streak: int
    max_streak: int
    # guess count (1-5) -> number of wins achieved on that guess
    guess_distribution: Dict[int, int]
    last_played_date: date | None = None
    # The guess number on which TODAY's puzzle was solved (None if today not
    # yet played or not solved) — used by the UI to highlight today's bar.
    today_solved_guess: int | None = None
