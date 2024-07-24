from sqlalchemy import select, and_

from db import async_session
from core import AppException
from ..models import Decision as DecisionModel
from ..schemas import Decision, DecisionNotification


class DecisionStorage:
    _table = DecisionModel

    @classmethod
    async def check_decision(cls, data: DecisionNotification) -> None:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.loan_id == data.loan_id,
                        cls._table.decision_uid == data.decision_uid
                    )
                )
            )
            decision = query.scalars().first()

        if not decision:
            raise AppException("decision_check.decision_not_found")

    @classmethod
    async def get_decision(cls, decision_uid: str) -> Decision:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.decision_uid == decision_uid)
            )
            decision = query.scalars().first()

        if not decision:
            raise AppException("get_decision.decision_not_found")

        return Decision.model_validate(decision)
