from typing import NoReturn

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

DEFAULT_ARGS = {
    "owner": "Denis",
    "email": "devsboom@gmail.com",
    "email_on_failure": True,
    "email_on_retry": False,
    "retry": 3,
    "retry_delay": timedelta(seconds=30)
}

dag = DAG(
    dag_id="mlops_dag_1",
    schedule_interval="0 1 * * *",
    start_date=days_ago(2),
    catchup=False,
    tags=["mlops"],
    default_args=DEFAULT_ARGS
)

name = "JR"


def init(ti) -> NoReturn:
    greeting = f"Hello {name}!"
    ti.xcom_push(key="init", value=greeting)


def get_data_from_init(ti) -> str:
    greeting = ti.xcom_pull(key="init")
    return f"{greeting} Welcome to the next level!"


task_init = PythonOperator(task_id="init",
                           op_kwargs={"name": "JR"},
                           python_callable=init,
                           dag=dag)


task_get_data_from_init = PythonOperator(task_id="get_data_from_init",
                                         python_callable=get_data_from_init,
                                         dag=dag)

task_init >> task_get_data_from_init
