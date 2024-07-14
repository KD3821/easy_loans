from datetime import date
from enum import Enum
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionType(str, Enum):
    DEBIT = "deposit"
    CREDIT = "credit"


class NewTransaction(BaseModel):
    date: date
    customer_id: int
    type: TransactionType
    amount: Decimal
    balance: Decimal
    category: str
    details: str

    model_config = ConfigDict(from_attributes=True)


class Transaction(NewTransaction):  # todo check if needed

    id: int
