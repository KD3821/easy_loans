from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Date, Integer, String, DateTime, Numeric, ForeignKey, JSON

from db import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    start_date = Column(Date)
    finish_date = Column(Date)
    debit = Column(Numeric(10, 2), nullable=True)
    credit = Column(Numeric(10, 2), nullable=True)
    txn_count = Column(Integer)
    risks = Column(JSON, nullable=True)
    processed_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    customer = relationship("Customer", back_populates="reports")

    # @property
    # def balance(self):
    #     if self.debit is None:
    #         self.debit = Decimal("0.00")
    #     if self.credit is None:
    #         self.credit = Decimal("0.00")
    #     return self.debit - self.credit
