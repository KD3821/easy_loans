from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Numeric
from sqlalchemy.ext.asyncio import AsyncSession

from db import Base


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
    employer = Column(String)
    monthly_income = Column(Numeric(8, 2))
    property_area = Column(String, default=URBAN)
    credit_history = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    loans = relationship("Loan", back_populates="customer")
    report_settings = relationship("ReportSettings", back_populates="customer")
