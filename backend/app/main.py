from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from urllib.parse import urlparse

from app.config import settings
from app.limiter import limiter
from app.routers import auth as auth_router
from app.routers import game as game_router
from app.routers import stats as stats_router

app = FastAPI(title="Bugdle")

# CORS is locked to the configured frontend origin (no wildcard) because a
# refresh token is issued as an httpOnly cookie and must not leak to arbitrary
# origins. `localhost` and `127.0.0.1` are distinct origins to the browser, so
# we accept both representations of FRONTEND_ORIGIN for local dev.
_allowed_origins = {settings.FRONTEND_ORIGIN}
_parsed = urlparse(settings.FRONTEND_ORIGIN)
if _parsed.hostname in ("localhost", "127.0.0.1"):
    _scheme = _parsed.scheme or "http"
    _port = f":{_parsed.port}" if _parsed.port else ""
    _allowed_origins.add(f"{_scheme}://localhost{_port}")
    _allowed_origins.add(f"{_scheme}://127.0.0.1{_port}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_allowed_origins),
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

