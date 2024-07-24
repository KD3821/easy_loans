import os
import json
import pickle
import logging
from datetime import timedelta
from typing import Dict, Any

import pandas as pd
import numpy as np
from airflow.models import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

BUCKET = os.getenv("BUCKET")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

AF_API_KEY = os.getenv("AF_API_KEY")
AF_WEBHOOK = os.getenv("AF_WEBHOOK")

_LOG = logging.getLogger()
_LOG.addHandler(logging.StreamHandler())

DEFAULT_ARGS = {
    "owner": "Denis",
    "email": "devsboom@gmail.com",
    "email_on_failure": False,
    "email_on_retry": False,
    "retry": 3,
    "retry_delay": timedelta(seconds=30)
}

dag = DAG(
    dag_id="decision",
    catchup=False,
    tags=["decision_ops"],
    default_args=DEFAULT_ARGS
)


def get_data_from_db(**kwargs) -> Dict[str, Any]:
    _LOG.info("Decision pipeline is initialized.")

    customer_id = kwargs.get("dag_run").conf.get("customer_id")
    loan_id = kwargs.get("dag_run").conf.get("loan_id")
    decision_uid = kwargs.get("dag_run").conf.get("decision_uid")
    analysis_start_date = kwargs.get("dag_run").conf.get("analysis_start_date")

    pg_hook = PostgresHook("pg_connection")
    conn = pg_hook.get_conn()

    customer_data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT gender, education, marital_status, children, self_employed, property_area, credit_history FROM"
            f" customers WHERE id = '{customer_id}';"
    )

    loan_data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT coapplicant_income, amount, month_term FROM loans WHERE id = '{loan_id}' AND "
            f"customer_id = '{customer_id}';"
    )

    report_data = pd.read_sql_query(
        con=conn,
        sql=f"SELECT risks, estimate_annual_income, risks_income_pct FROM reports WHERE customer_id = '{customer_id}' "
            f"AND finish_date >= '{analysis_start_date}';"
    )

    s3_hook = S3Hook("s3_connector")
    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")

    json_customer_object = json.dumps(customer_data.to_dict(), indent=4)
    resource.Object(BUCKET, f"decision_customers/{decision_uid}.json").put(Body=json_customer_object)

    json_loan_object = json.dumps(loan_data.to_dict(), indent=4)
    resource.Object(BUCKET, f"decision_loans/{decision_uid}.json").put(Body=json_loan_object)

    json_report_object = json.dumps(report_data.to_dict(), indent=4)
    resource.Object(BUCKET, f"decision_reports/{decision_uid}.json").put(Body=json_report_object)

    decision_dict = {
        'ApplicantIncome': int(0),
        'CoapplicantIncome': float(0),
        'LoanAmount': float(0),
        'Loan_Amount_Term': float(0),
        'Credit_History': float(0),
        'LoanAmount_log': float(0),
        'Gender_Female': False,
        'Gender_Male': False,
        'Married_No': False,
        'Married_Yes': False,
        'Dependents_0': False,
        'Dependents_1': False,
        'Dependents_2': False,
        'Dependents_3+': False,
        'Education_Graduate': False,
        'Education_Not Graduate': False,
        'Self_Employed_No': False,
        'Self_Employed_Yes': False,
        'Property_Area_Rural': False,
        'Property_Area_Semiurban': False,
        'Property_Area_Urban': False
    }

    decision_props = {
        "loan_id": loan_id,
        "decision_uid": decision_uid,
        "decision_dict": decision_dict
    }

    return decision_props


def transform_customer_data(**kwargs) -> Dict[str, Any]:
    ti = kwargs.get("ti")
    decision_props = ti.xcom_pull(task_ids="get_data_from_db")
    decision_uid = decision_props.get("decision_uid")
    decision_dict = decision_props.get("decision_dict")

    s3_hook = S3Hook("s3_connector")
    file = s3_hook.download_file(key=f"decision_customers/{decision_uid}.json", bucket_name=BUCKET)
    data = pd.read_json(file)

    def prepare_customer_data(customer_data, final_dict):
        if customer_data["gender"].loc[0] == "male":
            final_dict["Gender_Male"] = True
        else:
            final_dict["Gender_Female"] = True

        if customer_data["education"].loc[0] == "school":
            final_dict["Education_Not Graduate"] = True
        else:
            final_dict["Education_Graduate"] = True

        if customer_data["marital_status"].loc[0] == "married":
            final_dict["Married_Yes"] = True
        else:
            final_dict["Married_No"] = True

        if customer_data["children"].loc[0] >= 3:
            final_dict["Dependents_3+"] = True
        elif customer_data["children"].loc[0] == 2:
            final_dict["Dependents_2"] = True
        elif customer_data["children"].loc[0] == 1:
            final_dict["Dependents_1"] = True
        else:
            final_dict["Dependents_0"] = True

        if customer_data["self_employed"].loc[0] is True:
            final_dict["Self_Employed_Yes"] = True
        else:
            final_dict["Self_Employed_No"] = True

        if customer_data["property_area"].loc[0] == 'city':
            final_dict["Property_Area_Urban"] = True
        elif customer_data["property_area"].loc[0] == 'town':
            final_dict["Property_Area_Semiurban"] = True
        else:
            final_dict["Property_Area_Rural"] = True

        if customer_data["credit_history"].loc[0] is True:
            final_dict["Credit_History"] = float(1)

        return final_dict

    decision_dict = prepare_customer_data(data, decision_dict)

    decision_props["decision_dict"] = decision_dict

    _LOG.info(f"Customer data successfully transformed.")

    return decision_props


def transform_loan_data(**kwargs) -> Dict[str, Any]:
    ti = kwargs.get("ti")
    decision_props = ti.xcom_pull(task_ids="transform_customer_data")
    decision_uid = decision_props.get("decision_uid")
    decision_dict = decision_props.get("decision_dict")

    s3_hook = S3Hook("s3_connector")
    file = s3_hook.download_file(key=f"decision_loans/{decision_uid}.json", bucket_name=BUCKET)
    data = pd.read_json(file)

    def prepare_loan_data(loan_data, final_dict):
        if pd.notna(loan_data.at[0, "coapplicant_income"]):
            final_dict["CoapplicantIncome"] = float(loan_data["coapplicant_income"].loc[0])

        final_dict["LoanAmount"] = float(loan_data["amount"].loc[0] / 1000)

        final_dict["LoanAmount_log"] = np.log(final_dict["LoanAmount"])

        final_dict["Loan_Amount_Term"] = float(loan_data["month_term"].loc[0])

        return final_dict

    decision_dict = prepare_loan_data(data, decision_dict)

    decision_props["decision_dict"] = decision_dict

    _LOG.info(f"Loan data successfully transformed.")

    return decision_props


def transform_report_data(**kwargs) -> Dict[str, Any]:
    ti = kwargs.get("ti")
    decision_props = ti.xcom_pull(task_ids="transform_loan_data")
    decision_uid = decision_props.get("decision_uid")
    decision_dict = decision_props.get("decision_dict")

    s3_hook = S3Hook("s3_connector")
    file = s3_hook.download_file(key=f"decision_reports/{decision_uid}.json", bucket_name=BUCKET)
    data = pd.read_json(file)

    def prepare_report_data(report_data, final_dict, decision_uid):
        final_dict["ApplicantIncome"] = int(report_data['estimate_annual_income'].median() / 12)

        risk_data = report_data.drop(['estimate_annual_income'], axis=1)
        risk_data = risk_data[risk_data['risks_income_pct'].notna()]

        if risk_data['risks'].count() == 0:
            risk_dict = {}
        else:
            risk_dict = {}
            risk_median = risk_data['risks_income_pct'].median()
            risk_dict[decision_uid] = risk_median

            risk_list = []
            for risks in risk_data['risks']:
                risk_list.extend(risks)

            risk_stats = pd.DataFrame(risk_list, columns=['id', 'amount', 'category', 'details'])
            stats = risk_stats.groupby('category').amount.sum().to_dict()

            ids = risk_stats.groupby(['category'])
            for k, v in ids.groups.items():
                risk_dict[k] = {'spent': stats.get(k), 'id_list': [risk_stats.loc[i, 'id'] for i in v]}

        return final_dict, risk_dict

    decision_dict, risks_dict = prepare_report_data(data, decision_dict, decision_uid)

    decision_props["decision_dict"] = decision_dict
    decision_props["risks_dict"] = risks_dict

    _LOG.info(f"Report data successfully transformed.")

    return decision_props


def process_model_prediction(**kwargs) -> Dict[str, Any]:
    ti = kwargs.get("ti")
    decision_props = ti.xcom_pull(task_ids="transform_report_data")
    loan_id = decision_props.get("loan_id")
    decision_uid = decision_props.get("decision_uid")
    decision_dict = decision_props.get("decision_dict")
    risks_dict = decision_props.get("risks_dict")

    s3_hook = S3Hook("s3_connector")

    file = s3_hook.download_file(key=f"models/LR.pkl", bucket_name=BUCKET)
    model = pickle.load(open(file, 'rb'))

    decision_df = pd.DataFrame.from_dict(decision_dict, orient='index')
    decision_df = decision_df.transpose()
    decision_proba = model.predict_proba(decision_df)

    decision_text = f"Customer is eligible for loan with probability of '{round(decision_proba[0][1], 2)}'."

    if risks_dict:
        risk_median = risks_dict.pop(decision_uid)
        risk_text = f" Median balance of risk transactions equals {risk_median} % of annual income. Details:"

        for k, v in risks_dict.items():
            risk_text += f" {k}: total spent of {v.get('spent')} (transaction_id {[i for i in v.get('id_list')]});"

        decision_text += risk_text

    data = pd.DataFrame(columns=["loan_id", "decision_uid", "decision_text"])

    data.loc[0] = [loan_id, decision_uid, decision_text]

    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    data.to_sql(name="decisions", con=engine, index=False, if_exists='append')

    json_byte_object = json.dumps(data.to_dict(), indent=4)
    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")
    resource.Object(BUCKET, f"decision_results/{decision_uid}.json").put(Body=json_byte_object)

    _LOG.info(f"Decision successfully stored in DB: {loan_id=}, {decision_uid=}.")

    return {"loan_id": loan_id, "decision_uid": decision_uid}


def notify_loan_analysed(**kwargs) -> None:
    ti = kwargs.get("ti")
    info = ti.xcom_pull(task_ids="process_model_prediction")
    loan_id = info.get("loan_id")
    decision_uid = info.get("decision_uid")

    http_hook = HttpHook(method="POST", http_conn_id="loans_connection")
    http_hook.run(
        endpoint=AF_WEBHOOK, json={"loan_id": loan_id, "decision_uid": decision_uid}, headers={"Apikey": AF_API_KEY}
    )

    _LOG.info(f"Notification is sent for: {loan_id=}, {decision_uid=}.")


task_get_data_from_db = PythonOperator(task_id="get_data_from_db",
                                       python_callable=get_data_from_db,
                                       provide_context=True,
                                       dag=dag)

task_transform_customer_data = PythonOperator(task_id="transform_customer_data",
                                              python_callable=transform_customer_data,
                                              provide_context=True,
                                              dag=dag)

task_transform_loan_data = PythonOperator(task_id="transform_loan_data",
                                          python_callable=transform_loan_data,
                                          provide_context=True,
                                          dag=dag)

task_transform_report_data = PythonOperator(task_id="transform_report_data",
                                            python_callable=transform_report_data,
                                            provide_context=True,
                                            dag=dag)

task_process_model_prediction = PythonOperator(task_id="process_model_prediction",
                                               python_callable=process_model_prediction,
                                               provide_context=True,
                                               dag=dag)

task_notify_loan_analysed = PythonOperator(task_id="notify_loan_analysed",
                                           python_callable=notify_loan_analysed,
                                           provide_context=True,
                                           dag=dag)

(task_get_data_from_db >> task_transform_customer_data >> task_transform_loan_data >> task_transform_report_data >>
 task_process_model_prediction >> task_notify_loan_analysed)
