from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Date, Integer, DateTime, Numeric, ForeignKey, JSON, Float

from db import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    start_date = Column(Date)
    finish_date = Column(Date)
    debit = Column(Numeric(10, 2), nullable=True)
    credit = Column(Numeric(10, 2), nullable=True)
    closing_balance = Column(Numeric(10, 2))
    txn_count = Column(Integer)
    estimate_annual_income = Column(Numeric(10, 2))
    risks = Column(JSON, nullable=True)
    risks_income_pct = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    customer = relationship("Customer", back_populates="reports")
