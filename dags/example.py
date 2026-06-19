from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "User",
    "depends_on_past": False,
    "start_date": datetime(2015, 12, 1),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "schedule_interval": "@daily",
}

dag = DAG("sample", catchup=False, default_args=default_args)

t1 = BashOperator(
    task_id="print_date",
    bash_command="date",
    dag=dag)

t2 = BashOperator(
    task_id="list_file",
    bash_command="gsutil ls",
    dag=dag)

t1 >> t2
