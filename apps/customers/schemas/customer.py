from typing import List
from decimal import Decimal
from datetime import datetime, timedelta

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class NewCustomer(BaseModel):
    fullname: str
    email: EmailStr
    gender: str
    birthdate: datetime
    education: str
    children: int
    self_employed: bool
    employer: str
    monthly_income: Decimal
    property_area: str
    credit_history: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("birthdate")
    def eighteen_years_age(cls, birthdate):  # noqa
        if birthdate > datetime.now() - timedelta(days=(365 * 18)):
            raise ValueError("Must be 18 years old to apply for loan.")
        return birthdate.date()


class Customer(NewCustomer):
    id: int


class CustomerList(BaseModel):
    total: int
    customers: List[Customer]
