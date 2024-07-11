from datetime import date

from pydantic import BaseModel, ConfigDict


class ReportDates(BaseModel):
    start_date: date
    finish_date: date


class ReportCreate(ReportDates):
    customer_id: int
