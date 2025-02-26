from airflow import DAG, Dataset
from airflow.decorators import task

from datetime import datetime

my_file = Dataset("/tmp/my_file.txt")
my_file_2 = Dataset("/tmp/my_file_2.txt")

with DAG(
    dag_id="producer",
    schedule="@daily",
    start_date=datetime(2022, 1 , 1),
    catchup=False
):

    @task(outlets=[my_file])   # This to tell the dateset to update the dataset
    def update_dateset():
        with open(my_file.uri, "a+") as f:
            f.write("producer update")

    # The lower @task "my_file_2" to show how to make datasets  dependency
    @task(outlets=[my_file_2])   # This to tell the dateset to update the dataset
    def update_dateset_2():
        with open(my_file_2.uri, "a+") as f:
            f.write("producer update")

    update_dateset() >> update_dateset_2()
