from airflow.decorators import task, dag
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

from docker.types import Mount


@dag(start_date=datetime(2024, 1, 1), schedule_interval="@daily", catchup=False)
def docker_dag():
    @task()
    def t1():
        pass

    t2 = DockerOperator(
        task_id='t2',
        api_version='auto',
        container_name='task_t2',   # For organizing dockers
        image='stock_image:v1.0.0',  # To choose which python run the docker network
        command='bash /tmp/scripts/output.sh ',
        docker_url='unix://var/run/docker.sock',
        # Unix Socket that dokcer demand listening to interact so docker run dag
        network_mode='bridge',  # Making an internal network
        xcom=True,
        retrieve_output=True,
        retrieve_output_path='/tmp/script.out',
        auto_remove=True,  # Will remove docker container created for the task
        mount_temp_dir=False,   # To be able to run docker inside a docker we need to use this to disable mount f(x)
        mounts=[
            Mount(source='/Users/Rakan Hoji/sandbox/includes/scripts', target='/tmp/scripts', type='bind')
        ]
    )

    t1() >> t2


dag = docker_dag()
