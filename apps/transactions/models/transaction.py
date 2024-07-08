from sqlalchemy import Column, Integer, String, Numeric, Date

from db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    email = Column(String)
    type = Column(String)
    amount = Column(Numeric(8, 2))
    balance = Column(Numeric(8, 2))
    category = Column(String)
    details = Column(String)
