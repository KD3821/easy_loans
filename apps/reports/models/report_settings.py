from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey

from db import Base


class ReportSettings(Base):
    __table__ = "report_settings"

    # PCT is for percentage from monthly_income
    FIRST_INCOME_PCT = 40
    SECOND_INCOME_PCT = (100 - FIRST_INCOME_PCT)
    STOP_SPENDING_AT_PCT = 5
    STARTING_BALANCE_PCT = (10, 20)
    FIRST_INCOME_DAYS = (5, 10)
    SECOND_INCOME_DAYS = (20, 25)
    RENTAL_RATE_PCT = 20

    RISKS = (
        ("online bookmaker", "1xBet"),
        ("microfinance", "Credit Expert"),
        ("online gambling", "Casino 777"),
    )

    id = Column(Integer, primary_key=True)
    customer_email = Column(String(128), ForeignKey('customers.email'))
    monthly_income = Column(Numeric(8, 2))
    starting_balance = Column(Numeric(8, 2))
    save_balance = Column(Numeric(8, 2))
    first_income_day = Column(Integer)
    second_income_day = Column(Integer)
    rental_rate = Column(Numeric(8, 2))
    employer = Column(String)
    have_risks = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    customer = relationship("Customer", back_populates="report_settings")
