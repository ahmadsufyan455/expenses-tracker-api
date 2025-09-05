from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from app.config.database import Base as SQLAlchemyBase


class Base(SQLAlchemyBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
