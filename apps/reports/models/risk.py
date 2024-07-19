from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, DateTime

from db import Base


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
