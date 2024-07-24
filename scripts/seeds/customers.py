import random

from apps.customers.models import Customer
from apps.reports.models import ReportSettings
from core import logger

from scripts.db_session import db_session


CUSTOMERS = [
    {
      "fullname": "Jeniffer Brown",
      "email": "jb@example.com",
      "gender": "female",
      "birthdate": "1987-12-12",
      "education": "college",
      "marital_status": "married",
      "children": 2,
      "self_employed": False,
      "employer": "Colorado & Co",
      "monthly_income": 5600,
      "property_area": "country",
      "credit_history": True
    },
    {
      "fullname": "John Donovan",
      "email": "johny_d@example.com",
      "gender": "male",
      "birthdate": "1980-07-05",
      "education": "college",
      "marital_status": "divorced",
      "children": 1,
      "self_employed": True,
      "employer": "Donovan's",
      "monthly_income": 7600,
      "property_area": "country",
      "credit_history": True
    }
]

REPORT_SETTINGS = {
    "jb@example.com": {
        "customer_id": 1,
        "employer": "Colorado & Co",
        "monthly_income": 5600,
        "starting_balance": (5600 * random.randint(*ReportSettings.STARTING_BALANCE_PCT) / 100),
        "save_balance": (5600 * ReportSettings.STOP_SPENDING_AT_PCT / 100),
        "rental_rate": (5600 * ReportSettings.RENTAL_RATE_PCT / 100),
        "first_income_day": random.randint(*ReportSettings.FIRST_INCOME_DAYS),
        "second_income_day": random.randint(*ReportSettings.SECOND_INCOME_DAYS),
        "have_risks": False
    },
    "johny_d@example.com": {
        "customer_id": 2,
        "employer": "Donovan's",
        "monthly_income": 7600,
        "starting_balance": (7600 * random.randint(*ReportSettings.STARTING_BALANCE_PCT) / 100),
        "save_balance": (7600 * ReportSettings.STOP_SPENDING_AT_PCT / 100),
        "rental_rate": (7600 * ReportSettings.RENTAL_RATE_PCT / 100),
        "first_income_day": random.randint(*ReportSettings.FIRST_INCOME_DAYS),
        "second_income_day": random.randint(*ReportSettings.SECOND_INCOME_DAYS),
        "have_risks": True
    }
}


def perform(*args, **kwargs):
    for customer in CUSTOMERS:
        email = customer.get("email")
        customer_exists = (
            db_session.query(Customer).filter_by(email=email).all()
        )

        if not customer_exists:
            db_session.add(Customer(**customer))
            db_session.add(ReportSettings(**REPORT_SETTINGS.get(email)))
        else:
            logger.info(f"Customer with {email=} already exists")

    db_session.commit()
    db_session.close()
