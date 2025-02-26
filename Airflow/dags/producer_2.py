from airflow import DAG
from airflow.decorators import task
from include.datasets import my_file

from datetime import datetime



with DAG(
        dag_id="producer",
        schedule="@daily",
        start_date=datetime(2022, 1, 1),
        catchup=False
):
    @task(outlets=[my_file])  # This to tell the dateset to update the dataset
    def update_my_file():
        None


    update_my_file()

