from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    active_date = Column(Date, nullable=False, unique=True)

    clues = relationship(
        "Clue",
        back_populates="scenario",
        order_by="Clue.order",
        cascade="all, delete-orphan",
    )
    attempts = relationship("Attempt", back_populates="scenario")
