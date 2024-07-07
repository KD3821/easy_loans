from datetime import datetime, timedelta

from pydantic import BaseModel, EmailStr, field_validator


class CustomerUpdate(BaseModel):
    fullname: str = None
    email: EmailStr = None
    gender: str = None
    birthdate: datetime = None
    education: str = None
    children: int = None
    self_employed: bool = None
    property_area: str = None
    credit_history: bool = None

    @field_validator("birthdate")
    def eighteen_years_age(cls, birthdate):  # noqa
        if birthdate > datetime.now() - timedelta(days=(365 * 18)):
            raise ValueError("Must be 18 years old to apply for loan.")
        return birthdate.date()
