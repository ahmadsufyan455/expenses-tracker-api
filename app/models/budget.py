from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .base import Base


class Budget(Base):
    __tablename__ = "budgets"

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    amount = Column(Integer)
    month = Column(Date, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    __table_args__ = (UniqueConstraint("user_id", "category_id", "month", name="uq_user_category_month"),
                      Index('idx_budget_user_category', 'user_id', 'category_id'),)
