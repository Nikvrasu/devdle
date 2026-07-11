from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.stats import StatsResponse
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def stats(user=Depends(get_current_user), db=Depends(get_db)):
    # Auth is REQUIRED: anonymous users have no persisted history to show.
    return stats_service.get_stats(db, user.id)
