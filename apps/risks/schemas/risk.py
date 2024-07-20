from typing import List

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RiskCreate(BaseModel):
    category: str
    details: str


class Risk(RiskCreate):
    id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RiskList(BaseModel):
    total: int
    risks: List[Risk]


class RiskUpdate(BaseModel):
    category: str | None = None
    details: str | None = None
