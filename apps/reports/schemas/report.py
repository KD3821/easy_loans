from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any

from pydantic import BaseModel, field_validator, ValidationInfo, ConfigDict


class ReportDates(BaseModel):
    start_date: date
    finish_date: date

    @field_validator("finish_date", "start_date")
    def date_sequence(cls, v: str, info: ValidationInfo):  # noqa
        if info.field_name == 'finish_date' and info.data.get('start_date'):
            s_date = info.data.get('start_date')
            if s_date > v:
                raise ValueError("finish date must later than start day.")
        if info.field_name == 'finish_date':
            if v > datetime.now().date():  # noqa
                raise ValueError("finish date must be no later than today.")
        return v


class ReportUploaded(BaseModel):
    id: int
    filename: str
    task_id: str


class ReportStatus(BaseModel):
    id: int
    status: str
    result: dict | None


class ReportDeleted(BaseModel):
    id: int
    task_id: str


class ReportResult(ReportDates):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    debit: Decimal
    credit: Decimal
    closing_balance: Decimal
    txn_count: int
    estimate_annual_income: Decimal
    risks: List[Dict[str, Any]] | None
    risks_income_pct: float | None
    analysis_id: str
    created_at: datetime
