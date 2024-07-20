from sqlalchemy import select, desc, asc, func

from db import async_session
from core import Pagination, PaginationOrder
from ..models import Risk as RiskModel
from ..schemas import RiskList, Risk


class RiskStorage:
    _table = RiskModel

    @classmethod
    async def get_many(cls, pagination: Pagination) -> RiskList:
        async with async_session() as session:
            order = desc if pagination.order == PaginationOrder.DESC else asc
            query = await session.execute(
                select(cls._table)
                .limit(pagination.per_page)
                .offset(pagination.page - 1 if pagination.page == 1 else (pagination.page - 1) * pagination.per_page)
                .order_by(order(cls._table.id))
            )
            result = query.scalars()
            count = await session.execute(
                select(func.count())
                .select_from(select(cls._table.id).subquery())
            )
            risk_count = count.scalar_one()

        risk_list = [Risk.model_validate(risk) for risk in result]

        return RiskList(total=risk_count, risks=risk_list)
