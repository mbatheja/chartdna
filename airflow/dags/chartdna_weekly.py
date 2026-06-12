from datetime import datetime, timedelta, timezone
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

default_args = {
    "owner": "chartdna",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}

dag = DAG(
    "chartdna_weekly_ingestion",
    default_args=default_args,
    description= "Weekly ingestion of Last.fm chart data",
    schedule_interval= "0 6 * * 1" ,
    start_date= datetime(2025, 1, 1, tzinfo=timezone.utc),
    catchup= False,
    tags= ["chartdna", "ingestion"]
)

def run_ingestion():
    from ingestion.fetch_charts import run
    run(limit=100)

with dag:
    ingest_task = PythonOperator(
        task_id="fetch_and_store_charts",
        python_callable=run_ingestion,
    )

    dbt_task = BashOperator(
        task_id="run_dbt_tasks",
        bash_command="source '/mnt/c/Users/Mahima Batheja/Project/chartdna/venv_linux/bin/activate' && cd '/mnt/c/Users/Mahima Batheja/Project/chartdna/chartdna_dbt' && dbt run && dbt test && dbt docs generate"

    )

    ingest_task >> dbt_task
