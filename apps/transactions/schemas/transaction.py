from datetime import date
from enum import Enum
from decimal import Decimal
from typing import List

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


class Transaction(NewTransaction):
    id: int


class TransactionList(BaseModel):
    total: int
    transactions: List[Transaction]


class TransactionUpdate(BaseModel):
    category: str | None = None
    details: str | None = None
