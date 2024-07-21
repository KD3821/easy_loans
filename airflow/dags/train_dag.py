import os
import json
import pickle
import logging
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, median_absolute_error, r2_score, accuracy_score
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


_LOG = logging.getLogger()
_LOG.addHandler(logging.StreamHandler())

train_csv = "train_data.csv"
datasets_dirname = "/home/dk/easy_loans/airflow/datasets"
train_results_dirname = "/home/dk/easy_loans/airflow/train_results"

BUCKET = "5e4f9aa0-52a3cd57-dc94-43c1-ae9a-f2724eeac656"
DATA_PATH = "datasets/loan_prediction.pkl"
TARGET = "Loan_Status"
FEATURES = ["Loan_ID", "Gender", "Married", "Dependents", "Education", "Self_Employed", "ApplicantIncome",
            "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History", "Property_Area", "Loan_Status"]

DEFAULT_ARGS = {
    "owner": "Denis",
    "email": "devsboom@gmail.com",
    "email_on_failure": True,
    "email_on_retry": False,
    "retry": 3,
    "retry_delay": timedelta(seconds=30)
}

dag = DAG(
    dag_id="train",
    schedule_interval="0 1 * * *",
    start_date=days_ago(2),
    catchup=False,
    tags=["mlops"],
    default_args=DEFAULT_ARGS
)


def init() -> None:
    _LOG.info("Train pipeline is initialized.")


def get_data_from_csv() -> None:
    data = pd.read_csv(os.path.join(datasets_dirname, train_csv))

    s3_hook = S3Hook("s3_connector")
    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")

    pickle_byte_obj = pickle.dumps(data)
    resource.Object(BUCKET, DATA_PATH).put(Body=pickle_byte_obj)

    _LOG.info("Train data upload finished")


def prepare_data() -> None:
    s3_hook = S3Hook("s3_connector")
    file = s3_hook.download_file(key=DATA_PATH, bucket_name=BUCKET)
    data = pd.read_pickle(file)

    X = data[FEATURES]

    X['Gender'].fillna(X['Gender'].mode()[0], inplace=True)
    X['Married'].fillna(X['Married'].mode()[0], inplace=True)
    X['Dependents'].fillna(X['Dependents'].mode()[0], inplace=True)
    X['Self_Employed'].fillna(X['Self_Employed'].mode()[0], inplace=True)
    X['Credit_History'].fillna(X['Credit_History'].mode()[0], inplace=True)
    X['Loan_Amount_Term'].fillna(X['Loan_Amount_Term'].mode()[0], inplace=True)
    X['LoanAmount'].fillna(X['LoanAmount'].median(), inplace=True)
    X['LoanAmount_log'] = np.log(X['LoanAmount'])
    X['Loan_Status'].replace('N', 0, inplace=True)
    X['Loan_Status'].replace('Y', 1, inplace=True)

    X = X.drop('Loan_ID', axis=1)
    y = X[TARGET]
    X = X.drop(TARGET, axis=1)

    X = pd.get_dummies(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")

    for name, data in zip(["X_train", "X_test", "y_train", "y_test"],
                          [X_train, X_test, y_train, y_test]):
        pickle_byte_obj = pickle.dumps(data)
        resource.Object(BUCKET, f"train_dataset/{name}.pkl").put(Body=pickle_byte_obj)

    _LOG.info("Data preparation finished")


def train_model() -> str:
    s3_hook = S3Hook("s3_connector")
    data = {}
    for name in ["X_train", "X_test", "y_train", "y_test"]:
        file = s3_hook.download_file(key=f"train_dataset/{name}.pkl", bucket_name=BUCKET)
        data[name] = pd.read_pickle(file)

        pd.DataFrame(data[name]).to_csv(os.path.join('/home/dk/easy_loans/airflow/check_splits', f'{name}.csv'),
                                        index=False)  # todo remove later

    model = LogisticRegression()
    model.fit(data["X_train"], data["y_train"])
    prediction = model.predict(data["X_test"])

    result = {}
    result["accuracy_score"] = accuracy_score(data["y_test"], prediction)
    result["r2_score"] = r2_score(data["y_test"], prediction)
    result["rmse"] = mean_squared_error(data["y_test"], prediction) ** 0.5
    result["mae"] = median_absolute_error(data["y_test"], prediction)

    date = datetime.now().strftime("%H-%M-%S_%Y-%m-%d")

    session = s3_hook.get_session("ru-1")
    resource = session.resource("s3")

    json_byte_object = json.dumps(result)
    resource.Object(BUCKET, f"train_results/{date}.json").put(Body=json_byte_object)

    pickle_byte_obj = pickle.dumps(model)
    resource.Object(BUCKET, f"models/LR.pkl").put(Body=pickle_byte_obj)

    _LOG.info("Model training finished")

    return date


def save_results(**kwargs) -> None:
    dir_path = Path(train_results_dirname)
    if not os.path.exists(dir_path):
        dir_path.mkdir(parents=True)

    ti = kwargs.get("ti")
    name = ti.xcom_pull(task_ids="train_model")
    s3_hook = S3Hook("s3_connector")
    result_file = s3_hook.download_file(key=f"train_results/{name}.json",
                                        bucket_name=BUCKET,
                                        local_path=dir_path,
                                        preserve_file_name=True,
                                        use_autogenerated_subdir=False)

    _LOG.info(f"Successfully downloaded result: {result_file}!")


task_init = PythonOperator(task_id="init", python_callable=init, dag=dag)
task_get_data = PythonOperator(task_id="get_data", python_callable=get_data_from_csv, dag=dag)
task_prepare_data = PythonOperator(task_id="prepare", python_callable=prepare_data, dag=dag)
task_train_model = PythonOperator(task_id="train_model", python_callable=train_model, dag=dag)
task_save_results = PythonOperator(task_id="save_results", python_callable=save_results, dag=dag, provide_context=True)


task_init >> task_get_data >> task_prepare_data >> task_train_model >> task_save_results
