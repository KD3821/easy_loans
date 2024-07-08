from datetime import datetime
from enum import Enum
from decimal import Decimal

from pydantic import BaseModel, EmailStr, ConfigDict


class TransactionType(str, Enum):
    DEBIT = "deposit"
    CREDIT = "credit"


class NewTransaction(BaseModel):
    date: datetime
    email: EmailStr
    type: TransactionType
    amount: Decimal
    balance: Decimal
    category: str
    details: str

    model_config = ConfigDict(from_attributes=True)


class Transaction(NewTransaction):

    id: int
