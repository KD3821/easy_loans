from typing import List

from sqlalchemy import select, and_

from db import async_session
from core import AppException
from ..models import Report as ReportModel
from ..schemas import ReportResult


class ReportStorage:
    _table = ReportModel

    @classmethod
    async def list_results(cls, customer_id: int) -> List[ReportResult]:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.customer_id == customer_id)
            )
            results = query.scalars()

        return [ReportResult.model_validate(result) for result in results]

    @classmethod
    async def get_result(cls, customer_id: int, analysis_id: str) -> ReportResult:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.customer_id == customer_id,
                        cls._table.analysis_id == analysis_id
                    )
                )
            )
            result = query.scalars().first()

            if result is None:
                raise AppException("analysis_result.analysis_result_not_found")

        return ReportResult.model_validate(result)
