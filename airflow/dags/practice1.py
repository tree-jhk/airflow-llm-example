# 사용할 Operator Import
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

default_args = {
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='simple_dag',
    default_args=default_args,
    description='Load texts, embed, and store embeddings',
    schedule_interval="@daily",
    tags=["BOAZ"],
    end_date=datetime(2023, 1, 5),
)

def simple_task(**kwargs):
    print("Simple task is running")

simple_task_operator = PythonOperator(
    task_id='simple_task',
    python_callable=simple_task,
    dag=dag,
)