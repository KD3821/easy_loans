from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    upload_id = Column(Integer, ForeignKey("transaction_uploads.id", ondelete="CASCADE"))
    type = Column(String)
    amount = Column(Numeric(8, 2))
    balance = Column(Numeric(8, 2))
    category = Column(String)
    details = Column(String)
    upload = relationship("TransactionUpload", back_populates="transactions")
