from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, String

from db import Base


class TransactionUpload(Base):
    __tablename__ = "transaction_uploads"

    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    task_id = Column(String)
    start_date = Column(Date)
    finish_date = Column(Date)
    status = Column(String, default=PROCESSING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    customer = relationship("Customer", back_populates="transaction_uploads")
    transactions = relationship("Transaction")
