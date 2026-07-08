from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True)
    # Nullable on purpose: anonymous play is supported (see Phase 2).
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    guesses_used = Column(Integer, nullable=False, default=0)
    solved = Column(Boolean, nullable=False, default=False)
    clues_revealed = Column(Integer, nullable=False, default=1)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="attempts")
    scenario = relationship("Scenario", back_populates="attempts")

    __table_args__ = (
        UniqueConstraint("user_id", "scenario_id", name="uq_user_scenario"),
    )
