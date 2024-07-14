from decimal import Decimal
from datetime import date

from pydantic import BaseModel, ConfigDict


class TransactionCelery(BaseModel):  # same as transactions.schemas.NewTransaction (to avoid circular import error)
    date: date
    customer_id: int
    upload_id: int
    type: str
    amount: Decimal
    balance: Decimal
    category: str
    details: str

    model_config = ConfigDict(from_attributes=True)
