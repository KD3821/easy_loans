import os
import json

from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def get_pd_json_customer(customer_id, date):
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    customer_data = pd.read_sql_query(
        con=engine,
        sql=f"SELECT gender, education, marital_status, children, self_employed, property_area, credit_history FROM"
            f" customers WHERE id = '{customer_id}';"
    )

    with open(f"{customer_id}_{date}_customer-data.json", "w") as f:
        json.dump(customer_data.to_dict(), f, indent=4)


def get_pd_json_loan(customer_id, loan_id, date):
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    loan_data = pd.read_sql_query(
        con=engine,
        sql=f"SELECT coapplicant_income, amount, month_term FROM loans WHERE id = '{loan_id}' AND "
            f"customer_id = '{customer_id}';"
    )

    with open(f"{customer_id}-{loan_id}_{date}_loan-data.json", "w") as f:
        json.dump(loan_data.to_dict(), f, indent=4)


def get_pd_json_report(customer_id, date):
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    loan_data = pd.read_sql_query(
        con=engine,
        sql=f"SELECT risks, estimate_annual_income, risks_income_pct FROM reports WHERE customer_id = '{customer_id}' "
            f"AND finish_date >= '{date}';"
    )

    with open(f"{customer_id}_{date}_report-data.json", "w") as f:
        json.dump(loan_data.to_dict(), f, indent=4)


get_pd_json_customer(4, "2024-04-30")
get_pd_json_loan(4, 6, "2024-04-30")
get_pd_json_report(4, "2024-04-30")


"""
run with command: python -m airflow.dev_scripts
"""