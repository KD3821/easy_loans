from sqlalchemy import select, desc, asc, func, and_

from db import async_session
from core import AppException, Pagination, PaginationOrder
from ..models import Risk as RiskModel
from ..schemas import RiskList, Risk, RiskCreate, RiskUpdate


class RiskStorage:
    _table = RiskModel

    @classmethod
    async def check_already_exist(cls, data: RiskCreate) -> None:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.category == data.category,
                        cls._table.details == data.details
                    )
                )
            )
            risk = query.scalars().first()

        if risk is not None:
            raise AppException("risk_store.risk_already_exist")

    @classmethod
    async def get_one(cls, risk_id) -> RiskModel:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table)
                .filter(cls._table.id == risk_id)
            )
            risk = query.scalars().first()

        if risk is None:
            raise AppException("get_risk.risk_not_found")

        return risk

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

    @classmethod
    async def create(cls, data: RiskCreate) -> Risk:
        await cls.check_already_exist(data)

        async with async_session() as session:
            new_risk = RiskModel(category=data.category, details=data.details)

            session.add(new_risk)
            await session.commit()
            await session.refresh(new_risk)

        return Risk.model_validate(new_risk)

    @classmethod
    async def update(cls, risk_id: int, data: RiskUpdate) -> Risk:
        risk = await cls.get_one(risk_id)
        await cls.check_already_exist(
            RiskCreate(
                category=data.category if data.category is not None else risk.category,
                details=data.details if data.details is not None else risk.details
            )
        )
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.id == risk_id)
            )
            risk = query.scalar_one()

            if data.category is not None:
                risk.category = data.category
            if data.details is not None:
                risk.details = data.details

            await session.commit()
            await session.refresh(risk)

        return Risk.model_validate(risk)

    @classmethod
    async def delete(cls, risk_id: int) -> None:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.id == risk_id)
            )
            risk = query.scalars().first()

            if risk is None:
                raise AppException("delete_risk.risk_not_found")

            await session.delete(risk)
            await session.commit()
