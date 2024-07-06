from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class NewCustomer(BaseModel):
    fullname: str
    email: EmailStr
    gender: str
    birthdate: datetime
    education: str
    children: int
    self_employed: bool
    property_area: str
    credit_history: bool

    model_config = ConfigDict(from_attributes=True)


class Customer(NewCustomer):
    id: int
