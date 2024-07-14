from decimal import Decimal
from datetime import datetime
from typing import Tuple, List

from pydantic import BaseModel, ConfigDict


class ReportSettingsCreate(BaseModel):
    customer_id: int
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


class ReportSettingsUpdate(BaseModel):
    monthly_income: Decimal | None
    employer: str | None


class ReportSettingsGenerate(ReportSettingsCreate):
    starting_balance: Decimal
    save_balance: Decimal
    first_income_day: int
    second_income_day: int
    rental_rate: Decimal
    have_risks: bool
    first_income: Decimal
    second_income: Decimal
    save_balance: Decimal
    risks: List[Tuple[str, str]]
