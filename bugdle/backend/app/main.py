from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import auth as auth_router
from app.routers import game as game_router
from app.routers import stats as stats_router

app = FastAPI(title="Bugdle")

# CORS is locked to the exact frontend origin (no wildcard) because a refresh
# token is issued as an httpOnly cookie in a later phase and must not leak to
# arbitrary origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (slowapi). Required on the guess endpoint to blunt brute-force.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(game_router.router)
app.include_router(auth_router.router)
app.include_router(stats_router.router)

