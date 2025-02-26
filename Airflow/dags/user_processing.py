from airflow import DAG
from datetime import datetime

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

import json
from pandas import json_normalize
from airflow import Dataset # To import DataSet

# Valid datasets:
'''
schemeless = Dataset("/path/file.txt")
csv_file = Dataset("file.csv")

my_file = Dataset(
    "s3://dataset/file.csv",
    extra={'owner','james'},
)
'''

# The task to run
def _process_user(ti): # This is needed to pull data
    user = ti.xcom_pull(task_ids='extract_user')
    user = user['results'][0]
    processed_user = json_normalize({
        'firstname': user['name']['first'],
        'lastname': user['name']['last'],
        'country': user['location']['country'],
        'username': user['login']['username'],
        'password': user['login']['password'],
        'email': user['email']

    })
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)

def _store_user():
    hook = postgresHook(postgres_conn_id='postgres')  # Hook is an Extracting Tool
    hook.copy_expert(  # To copy from sql into the file
        sql="COPY users FROM stdin WITH DELIMITER as ','",
        filename='/tmp/processed_user.csv'  # Copy Users from this csv file into the table users ^^^
    )

with DAG(
        dag_id="user_processing",
        start_date=datetime(2023, 1, 1),
        schedule_interval="@daily",
        catchup=False # Catchup is for Back-filling historical data

) as dag:

    create_table = PostgresOperator(     # This table gets filled by _store_user():
        task_id='create_table',
        postgres_conn_id='postgres',
        sql='''
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
                );
            '''
    )

    is_api_available = HttpSensor(
        task_id='is_api_available',
        http_conn_id='user_api',
        endpoint='api/'

    )

    extract_user = SimpleHttpOperator(
        task_id='extract_user',
        http_conn_id='user_api',
        endpoint='api/',
        method='GET',    # To not send any data
        response_filter=lambda response: json.loads(response.text), # to extract the data and send it in json file
        log_response=True
    )

    process_user = PythonOperator(      # To Run it
        task_id='process_user',
        python_callable=_process_user
    )

   # extract_user >> process_user

    store_user = PythonOperator(        # To Run it
        task_id='store_user',
        python_callable=_store_user
    )

    # indicate which task to be done first
    create_table >> is_api_available >> extract_user >> process_user >> store_user
