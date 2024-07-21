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


def get_transactions_from_db(**kwargs) -> Dict[str, Any]:
    _LOG.info("Analysis pipeline is initialized.")

    customer_id = kwargs.get("dag_run").conf.get("customer_id")
    upload_id = kwargs.get("dag_run").conf.get("upload_id")
    upload_start_date = kwargs.get("dag_run").conf.get("upload_start_date")
    upload_finish_date = kwargs.get("dag_run").conf.get("upload_finish_date")
    analysis_id = kwargs.get("dag_run").conf.get("analysis_id")

    pg_hook = PostgresHook("pg_connection")
    conn = pg_hook.get_conn()

    data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT * FROM transactions WHERE customer_id = '{customer_id}' AND upload_id = '{upload_id}';"
    )
    data["date"] = pd.to_datetime(data["date"], infer_datetime_format=True).dt.strftime("%Y-%m-%d")

    s3_hook = S3Hook("s3_connector")
    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")
    json_byte_object = json.dumps(data.to_dict(orient='records'), indent=4)
    resource.Object(BUCKET, f"transactions/{analysis_id}.json").put(Body=json_byte_object)

    _LOG.info("Transactions for analysis successfully uploaded.")

    analysis_props = {
        "customer_id": customer_id,
        "upload_id": upload_id,
        "analysis_id": analysis_id,
        "upload_start_date": upload_start_date,
        "upload_finish_date": upload_finish_date,
        "risks": False
    }

    return analysis_props


def check_risk_transactions(**kwargs) -> Dict[str, Any]:
    ti = kwargs.get("ti")
    analysis_props = ti.xcom_pull(task_ids="get_transactions_from_db")
    analysis_id = analysis_props.get("analysis_id")

    s3_hook = S3Hook("s3_connector")
    file = s3_hook.download_file(key=f"transactions/{analysis_id}.json", bucket_name=BUCKET)
    data = pd.read_json(file)

    pg_hook = PostgresHook("pg_connection")
    conn = pg_hook.get_conn()
    risks = pd.read_sql_query(sql=f"SELECT category, details FROM risks;", con=conn)

    look_for_category = set(risks['category'].to_list())
    look_for_details = set(risks['details'].to_list())

    found_cat = data[data["category"].isin(look_for_category)].index
    risks_by_cat = data.loc[found_cat, :]

    found_details = data[data["details"].isin(look_for_details)].index
    risks_by_details = data.loc[found_details, :]

    total_risks = pd.concat([risks_by_details, risks_by_cat], axis=0).drop_duplicates()

    if total_risks.shape[0] != 0:
        analysis_props['risks'] = True
        total_risks["date"] = pd.to_datetime(total_risks["date"], infer_datetime_format=True).dt.strftime("%Y-%m-%d")
        json_byte_object = json.dumps(total_risks.to_dict(), indent=4)
        session = s3_hook.get_session("ru-1")
        resource = session.resource("s3")
        resource.Object(BUCKET, f"risks/{analysis_id}.json").put(Body=json_byte_object)

    _LOG.info(f"Transactions successfully checked for risks.")

    return analysis_props


def calculate_report(**kwargs) -> Dict[str, Any]:
    ti = kwargs.get("ti")
    analysis_props = ti.xcom_pull(task_ids="check_risk_transactions")
    analysis_id = analysis_props.get("analysis_id")
    start_date_str = analysis_props.get("upload_start_date")
    finish_date_str = analysis_props.get("upload_finish_date")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    finish_date = datetime.strptime(finish_date_str, "%Y-%m-%d").date()

    s3_hook = S3Hook("s3_connector")
    txn_file = s3_hook.download_file(key=f"transactions/{analysis_id}.json", bucket_name=BUCKET)
    data = pd.read_json(txn_file)

    txn_count = data.shape[0]
    diff = data.groupby('type').amount.sum()
    spent = diff.credit
    earned = diff.deposit
    closing_balance = earned - spent

    period = finish_date - start_date
    days = period.days
    est_annual_income = earned / days * 365

    if analysis_props.get("risks"):
        s3_hook = S3Hook("s3_connector")
        risk_file = s3_hook.download_file(key=f"risks/{analysis_id}.json", bucket_name=BUCKET)
        risks = pd.read_json(risk_file)
        risks_amount = risks.amount.sum()
        risks_income_pct = round(risks_amount * 100 / earned, 2)
        risks.drop(["customer_id", "upload_id"], axis=1, inplace=True)
        risks["date"] = pd.to_datetime(risks["date"], infer_datetime_format=True).dt.strftime("%Y-%m-%d")
        risks_list = risks.to_dict(orient="records")
    else:
        risks_list = []
        risks_income_pct = None

    report_dict = {
        "customer_id": analysis_props.get("customer_id"),
        "start_date":  start_date_str,
        "finish_date": finish_date_str,
        "debit": earned,
        "credit": spent,
        "closing_balance": closing_balance,
        "txn_count": txn_count,
        "estimate_annual_income": est_annual_income,
        "risks_income_pct": risks_income_pct,
        "risks": risks_list
    }

    json_byte_object = json.dumps(report_dict, indent=4)
    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")
    resource.Object(BUCKET, f"analysis/{analysis_id}.json").put(Body=json_byte_object)

    _LOG.info(f"Report successfully calculated and uploaded.")

    return analysis_props


def finalize_report(**kwargs) -> None:
    ti = kwargs.get("ti")
    analysis_props = ti.xcom_pull(task_ids="calculate_report")
    analysis_id = analysis_props.get("analysis_id")

    s3_hook = S3Hook("s3_connector")
    analysis_file = s3_hook.download_file(key=f"analysis/{analysis_id}.json", bucket_name=BUCKET)

    data = pd.read_json(analysis_file, typ="series")

    risks = data["risks"]
    if risks:
        risks = list(map(
            lambda x: {"id": x.get("id"), "amount": x.get("amount"), "details": x.get("details")}, risks
        ))
    else:
        risks = None

    data.drop(["risks"], inplace=True)
    data = pd.DataFrame(data).transpose()
    data["risks"] = None

    if risks:
        data.at[0, "risks"] = risks
        data["risks"] = list(map(lambda x: json.dumps(x), data["risks"]))

    data["analysis_id"] = analysis_id

    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    data.to_sql(name="reports", con=engine, index=False, if_exists='append')

    _LOG.info(f"Report successfully stored in DB.")


task_get_transactions_from_db = PythonOperator(task_id="get_transactions_from_db",
                                               python_callable=get_transactions_from_db,
                                               provide_context=True,
                                               dag=dag)

task_check_risk_transactions = PythonOperator(task_id="check_risk_transactions",
                                              python_callable=check_risk_transactions,
                                              provide_context=True,
                                              dag=dag)

task_calculate_report = PythonOperator(task_id="calculate_report",
                                       python_callable=calculate_report,
                                       provide_context=True,
                                       dag=dag)

task_finalize_report = PythonOperator(task_id="finalize_report",
                                      python_callable=finalize_report,
                                      provide_context=True,
                                      dag=dag)


task_get_transactions_from_db >> task_check_risk_transactions >> task_calculate_report >> task_finalize_report
