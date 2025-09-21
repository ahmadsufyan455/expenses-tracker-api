from enum import Enum
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint, Index, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base


class PredictionType(Enum):
    DAILY = "daily"
    WEEKENDS = "weekends"
    WEEKDAYS = "weekdays"
    CUSTOM = "custom"


class Budget(Base):
    __tablename__ = "budgets"

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    amount = Column(Integer)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)

    # Prediction fields
    prediction_enabled = Column(Boolean, default=False, nullable=False)
    prediction_type = Column(SQLEnum(PredictionType), nullable=True)
    prediction_days_count = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    __table_args__ = (Index('idx_budget_user_category', 'user_id', 'category_id'),
                      Index('idx_budget_date_range', 'user_id', 'category_id', 'start_date', 'end_date'),)
