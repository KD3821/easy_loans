from decimal import Decimal
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoanId(BaseModel):
    id: int


class LoanStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    ANALYSED = "analysed"
    APPROVED = "approved"
    DECLINED = "declined"


class LoanCreate(BaseModel):
    amount: Decimal
    month_term: int
    coapplicant_fullname: str | None = None
    coapplicant_income: Decimal | None = None

    @field_validator("coapplicant_fullname")
    def validate_coapplicant_fullname(cls, v: str):
        if v is not None:
            names = v.strip().split(' ')
            if len(names) < 2:
                raise ValueError("Coapplicant fullname must include firstname and lastname")
            for name in names:
                if len(name) < 2:
                    raise ValueError("Copplicant names should have at least 2 letters")
        return v

    @field_validator("month_term")
    def validate_month_term(cls, v: int):
        if v < 12:
            raise ValueError("Minimal month_term is 12 month")
        return v


class Loan(LoanCreate, LoanId):
    customer_id: int
    status: LoanStatus
    decision_uid: str | None
    processed_by: EmailStr
    created_at: datetime
    updated_at: datetime | None
    finalized_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class LoanUpdate(LoanCreate):
    amount: Decimal | None = None
    month_term: int | None = None
    coapplicant_fullname: str | None = None
    coapplicant_income: Decimal | None = None


class LoanStatusUpdate(BaseModel):
    status: LoanStatus
    decision_uid: str


class LoanFinal(BaseModel):
    status: LoanStatus

    @field_validator("status")
    def validate_final_status(cls, v: str):
        if v not in (LoanStatus.APPROVED, LoanStatus.DECLINED):
            raise ValueError("Final loan status must be 'approved' or 'declined'.")
        return v
