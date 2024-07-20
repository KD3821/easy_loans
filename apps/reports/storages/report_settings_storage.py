import random
from decimal import Decimal

from sqlalchemy import select

from db import async_session
from ..models.report_settings import ReportSettings as ReportSettingsModel
from ..schemas.report_settings import (
    ReportSettingsCreate,
    ReportSettings,
    ReportSettingsUpdate,
    ReportSettingsGenerate
)


class ReportSettingsStorage:
    _table = ReportSettingsModel

    @classmethod
    async def get_report_settings(cls, customer_id: int) -> ReportSettingsGenerate:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.customer_id == customer_id)
            )
            report_settings = query.scalars().first()

            first_income = report_settings.monthly_income * cls._table.FIRST_INCOME_PCT / 100
            second_income = report_settings.monthly_income * cls._table.SECOND_INCOME_PCT / 100

        return ReportSettingsGenerate(
            customer_id=report_settings.customer_id,
            monthly_income=report_settings.monthly_income,
            employer=report_settings.employer,
            starting_balance=report_settings.starting_balance,
            save_balance=report_settings.save_balance,
            first_income_day=report_settings.first_income_day,
            second_income_day=report_settings.second_income_day,
            rental_rate=report_settings.rental_rate,
            have_risks=report_settings.have_risks,
            first_income=first_income,
            second_income=second_income
        )

    @classmethod
    async def calculate_settings(cls, monthly_income: Decimal) -> dict:
        calculation = {
            "monthly_income": monthly_income,
            "starting_balance": monthly_income * random.randint(*cls._table.STARTING_BALANCE_PCT) / 100,
            "save_balance": monthly_income * cls._table.STOP_SPENDING_AT_PCT / 100,
            "rental_rate": monthly_income * cls._table.RENTAL_RATE_PCT / 100,
            "first_income_day": random.randint(*cls._table.FIRST_INCOME_DAYS),
            "second_income_day":  random.randint(*cls._table.SECOND_INCOME_DAYS),
            "have_risks": random.randint(0, 1)
        }
        return calculation

    @classmethod
    async def create(cls, data: ReportSettingsCreate) -> ReportSettings:

        calculation = await cls.calculate_settings(data.monthly_income)

        async with async_session() as session:
            report_settings_model = cls._table(
                customer_id=data.customer_id,
                employer=data.employer,
                monthly_income=calculation.get("monthly_income"),
                starting_balance=calculation.get("starting_balance"),
                save_balance=calculation.get("save_balance"),
                rental_rate=calculation.get("rental_rate"),
                first_income_day=calculation.get("first_income_day"),
                second_income_day=calculation.get("second_income_day"),
                have_risks=calculation.get("have_risks")
            )

            session.add(report_settings_model)
            await session.commit()
            await session.refresh(report_settings_model)

        return ReportSettings.model_validate(report_settings_model)

    @classmethod
    async def update(cls, customer_id: int, data: ReportSettingsUpdate) -> ReportSettings:

        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.customer_id == customer_id)
            )
            report_settings = query.scalars().first()

            if data.employer is not None:
                report_settings.employer = data.employer

            if data.monthly_income is not None and report_settings.monthly_income != data.monthly_income:
                calculation = await cls.calculate_settings(data.monthly_income)

                for field, value in calculation.items():
                    setattr(report_settings, field, value)

            await session.commit()

        return ReportSettings.model_validate(report_settings)
