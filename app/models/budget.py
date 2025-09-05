from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.config.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Integer)
    month = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    __table_args__ = (UniqueConstraint("user_id", "category_id", "month", name="uq_user_category_month"),)
