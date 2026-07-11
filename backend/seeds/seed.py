import json
import os
from datetime import date

import app.models  # noqa: F401  (register models on Base.metadata)
from app.database import SessionLocal
from app.models.scenario import Scenario
from app.models.clue import Clue


def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed(db, data):
    inserted = 0
    for s in data.get("scenarios", []):
        # Idempotent: skip if a scenario already exists for this active_date.
        existing = (
            db.query(Scenario)
            .filter(Scenario.active_date == s["active_date"])
            .first()
        )
        if existing is not None:
            continue
        scenario = Scenario(
            answer=s["answer"],
            category=s["category"],
            difficulty=s["difficulty"],
            active_date=date.fromisoformat(s["active_date"]),
        )
        for order, text in enumerate(s["clues"], start=1):
            scenario.clues.append(Clue(order=order, text=text))
        db.add(scenario)
        inserted += 1
    db.commit()
    return inserted


def main():
    data = load_data()
    db = SessionLocal()
    try:
        n = seed(db, data)
        print(f"Seeded {n} new scenario(s); {len(data.get('scenarios', []))} total in source.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
