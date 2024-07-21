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
    customer_id = Column(Integer, ForeignKey('customers.id'))
    coapplicant_fullname = Column(String)
    coapplicant_income = Column(Numeric(8, 2))
    amount = Column(Numeric(8, 2))
    month_term = Column(Integer)
    status = Column(String, default=CREATED)
    decision_uid = Column(String, nullable=True)
    processed_by = Column(String, ForeignKey('users.email'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    customer = relationship("Customer", back_populates="loans")
