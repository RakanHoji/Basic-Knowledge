from airflow import DAG
from airflow.decorators import task
from include.datasets import my_file

from datetime import datetime



with DAG(
        dag_id="consumer",  # in schedule, it will wait for two datasets to update before ready
        schedule=[my_file, my_file_2],  # File name is used to so can be triggered when the update it's done by producer
        start_date=datetime(2022, 1, 1),
        catchup=False
):
    @task
    def read_dateset():
        with open(my_file.uri, "r") as f:
            print(f.read())


    read_dateset()
