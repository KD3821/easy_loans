import os
import json
import logging
from datetime import timedelta, datetime
from typing import Dict, Any

import pandas as pd
from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

_LOG = logging.getLogger()
_LOG.addHandler(logging.StreamHandler())

BUCKET = "5e4f9aa0-52a3cd57-dc94-43c1-ae9a-f2724eeac656"

DEFAULT_ARGS = {
    "owner": "Denis",
    "email": "devsboom@gmail.com",
    "email_on_failure": True,
    "email_on_retry": False,
    "retry": 3,
    "retry_delay": timedelta(seconds=30)
}

dag = DAG(
    dag_id="analysis",
    schedule_interval="0 1 * * *",
    start_date=days_ago(2),
    catchup=False,
    tags=["mlops"],
    default_args=DEFAULT_ARGS
)


def get_loan_request_data(**kwargs) -> Dict[str, Any]:
    _LOG.info("Loan request pipeline is initialized.")

    customer_id = kwargs.get("dag_run").conf.get("customer_id")
    loan_id = kwargs.get("dag_run").conf.get("loan_id")

    pg_hook = PostgresHook("pg_connection")
    conn = pg_hook.get_conn()

    customer_data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT * FROM customers WHERE id = '{customer_id}';"
    )
    customer_data["birthdate"] = pd.to_datetime(customer_data["birthdate"], infer_datetime_format=True).dt.strftime("%Y-%m-%d")

    loan_data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT * FROM loans WHERE id = '{loan_id}';"
    )

    report_data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT analysis_id FROM reports WHERE customer_id = '{customer_id}';"
    )

    # todo combine necessary data and upload