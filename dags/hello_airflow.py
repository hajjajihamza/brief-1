from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime


def hello():
    print("Hello from Airflow!")


with DAG(
    dag_id="hello_airflow",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    task = PythonOperator(
        task_id="hello_task",
        python_callable=hello,
    )