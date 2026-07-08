from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Clue(Base):
    __tablename__ = "clues"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    order = Column(Integer, nullable=False)
    text = Column(String, nullable=False)

    scenario = relationship("Scenario", back_populates="clues")

    __table_args__ = (
        UniqueConstraint("scenario_id", "order", name="uq_scenario_clue_order"),
    )
