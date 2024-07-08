from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean

from db import Base
from apps.loans.models import Loan
from apps.transactions.models import Transaction


class Customer(Base):
    __tablename__ = "customers"

    MALE = "male"
    FEMALE = "female"
    SCHOOL = "school"
    COLLEGE = "college"
    UNIVERSITY = "university"
    MARRIED = "married"
    UNMARRIED = "unmarried"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    URBAN = "city"
    RURAL = "country"

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    email = Column(String, unique=True)
    gender = Column(String)
    birthdate = Column(Date)
    education = Column(String, default=SCHOOL)
    children = Column(Integer, default=0)
    self_employed = Column(Boolean)
    property_area = Column(String, default=URBAN)
    credit_history = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    loans = relationship("Loan", back_populates="customer", foreign_keys=[Loan.customer_id])
