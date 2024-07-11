from decimal import Decimal
from datetime import datetime, timedelta, date

from pydantic import BaseModel, EmailStr, field_validator


class CustomerUpdate(BaseModel):
    fullname: str = None
    email: EmailStr = None
    gender: str = None
    birthdate: date = None
    education: str = None
    children: int = None
    self_employed: bool = None
    employer: str = None
    monthly_income: Decimal = None
    property_area: str = None
    credit_history: bool = None

    @field_validator("birthdate")
    def eighteen_years_age(cls, birthdate):  # noqa
        age_date = datetime.now() - timedelta(days=(365 * 18))
        if birthdate > age_date.date():
            raise ValueError("Must be 18 years old to apply for loan.")
        return birthdate
