from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DecisionId(BaseModel):
    id: int


class DecisionNotification(BaseModel):
    loan_id: int
    decision_uid: str


class Decision(DecisionNotification, DecisionId):
    decision_text: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
