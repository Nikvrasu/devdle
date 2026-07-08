from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.scenario import Scenario


def get_stats(db: Session, user_id: int) -> dict:
    rows = (
        db.query(Attempt, Scenario.active_date)
        .join(Scenario, Attempt.scenario_id == Scenario.id)
        .filter(Attempt.user_id == user_id)
        .all()
    )

    # A game counts as "completed" only when it ended: solved, OR all 5 guesses
    # used. In-progress attempts (solved=False, guesses_used<5) are ignored.
    completed = [(a, d) for a, d in rows if a.solved or a.guesses_used >= 5]
    games_played = len(completed)
    solved_rows = [(a, d) for a, d in rows if a.solved]
    win_rate = (len(solved_rows) / games_played) if games_played else 0.0

    # Distribution: bucket each solved attempt by the guess number it was won on.
    guess_distribution = {i: 0 for i in range(1, 6)}
    for a, _ in solved_rows:
        guess_distribution[a.guesses_used] = guess_distribution.get(a.guesses_used, 0) + 1

    # Per-day solved flag, keyed by active_date (unique per user per day).
    day_solved = {}
    for a, d in completed:
        day_solved[d] = a.solved

    last_played_date = max(day_solved.keys()) if day_solved else None

    # Today's solved guess number (for UI highlight), if today was played & solved.
    today = date.today()
    today_solved_guess = None
    for a, d in completed:
        if d == today and a.solved:
            today_solved_guess = a.guesses_used
            break

    # ----------------------------------------------------------------------
    # STREAK LOGIC (the trickiest part). Streaks are computed by active_date,
    # NOT created_at. Walk calendar days; a missing day OR an unsolved
    # completed day breaks the streak.
    # ----------------------------------------------------------------------

    # current_streak: walk backward from the most recent completed day.
    current_streak = 0
    played_desc = sorted(day_solved.keys(), reverse=True)
    if played_desc:
        expected = played_desc[0]
        for d in played_desc:
            if d != expected:
                break  # gap day -> streak ends
            if not day_solved[d]:
                break  # an unsolved completed day ends the streak
            current_streak += 1
            expected = d - timedelta(days=1)

    # max_streak: longest run of consecutive solved days anywhere in history.
    max_streak = 0
    run = 0
    expected_next = None
    for d in sorted(day_solved.keys()):
        if not day_solved[d]:
            run = 0
            expected_next = None
            continue
        if expected_next is None or d == expected_next:
            run += 1
        else:
            run = 1  # gap -> start a fresh run here
        expected_next = d + timedelta(days=1)
        max_streak = max(max_streak, run)

    return {
        "games_played": games_played,
        "win_rate": win_rate,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "guess_distribution": guess_distribution,
        "last_played_date": last_played_date,
        "today_solved_guess": today_solved_guess,
    }
