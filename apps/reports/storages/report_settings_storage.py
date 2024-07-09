import random

from db import async_session
from ..models.report_settings import ReportSettings as ReportSettingsModel
from ..schemas.report_settings import ReportSettingsCreate, ReportSettings


class ReportSettingsStorage:
    _table = ReportSettingsModel

    @classmethod
    async def create(cls, data: ReportSettingsCreate) -> ReportSettings:

        starting_balance = data.monthly_income * random.randint(*cls._table.STARTING_BALANCE_PCT) / 100
        save_balance = data.monthly_income * cls._table.STOP_SPENDING_AT_PCT / 100
        rental_rate = data.monthly_income * cls._table.RENTAL_RATE_PCT / 100
        first_income_day = random.randint(*cls._table.FIRST_INCOME_DAYS)
        second_income_day = random.randint(*cls._table.SECOND_INCOME_DAYS)
        have_risk = random.randint(0, 1)

        async with async_session() as session:
            report_settings_model = cls._table(
                customer_email=data.email,
                monthly_income=data.monthly_income,
                employer=data.employer,
                starting_balance=starting_balance,
                save_balance=save_balance,
                rental_rate=rental_rate,
                first_income_day=first_income_day,
                second_income_day=second_income_day,
                have_risk=have_risk
            )

            session.add(report_settings_model)
            await session.commit()

        return ReportSettings.model_validate(report_settings_model)
