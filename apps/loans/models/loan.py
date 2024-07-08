from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey

from db import Base


class Loan(Base):
    __tablename__ = "loans"

    CREATED = 'created'
    PROCESSING = 'processing'
    APPROVED = 'approved'
    DECLINED = 'declined'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('users.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship('Customer', back_populates="loans", foreign_keys=[customer_id])
    monthly_income = Column(Numeric(8, 2))
    coapplicant_income = Column(Numeric(8, 2))
    amount = Column(Numeric(8, 2))
    month_term = Column(Integer)
    status = Column(String, default=CREATED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    finalized_at = Column(DateTime(timezone=True), nullable=True)
