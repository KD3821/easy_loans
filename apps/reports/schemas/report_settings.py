from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class ReportSettingsCreate(BaseModel):
    customer_email: EmailStr
    monthly_income: Decimal
    employer: str


class ReportSettings(ReportSettingsCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    starting_balance: Decimal
    save_balance: Decimal
    first_income_day: int
    second_income_day: int
    rental_rate: Decimal
    have_risks: bool
    created_at: datetime
    updated_at: datetime | None
