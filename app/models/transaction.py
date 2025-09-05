from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


class PaymentMethod(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"


class Transaction(Base):
    __tablename__ = "transactions"

    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Integer)
    type = Column(SQLEnum(TransactionType), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
