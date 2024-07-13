from datetime import date, datetime

from pydantic import BaseModel, field_validator, ValidationInfo


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
