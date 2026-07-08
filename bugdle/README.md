# Bugdle

Bugdle is a Wordle-style daily game where players diagnose a software bug from
progressively revealed clues. The backend is FastAPI + SQLAlchemy + PostgreSQL;
the frontend is React + Vite + Tailwind.

## Backend (local)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # then fill in real values
uvicorn app.main:app --reload
```

## Frontend (local)

```bash
cd frontend
npm install
npm run dev
```
