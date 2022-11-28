from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models.baseoperator import chain, cross_downstream
from datetime import datetime,timedelta
from airflow.utils.dates import days_ago
from airflow.sensors.filesystem import FileSensor

# dag = DAG(...)
# task_1 = Operator(dag=dag)
# task_2 = Operator(dag=dag)

# schedule_interval="@daily", schedule_interval="*/10 * * * *",schedule_interval=timedelta(days=1)

# mail only works after adding SMTP server connection
default_args ={
    'retries' : 1,
    'retry_delay' : timedelta(minutes=1),
    'email_on_failure': True,
    'email_on_retry': True,
    'email': 'nainawaprachi@gmail.com',

}

# with DAG(dag_id='taniya_dag', schedule_interval="@daily", default_args=default_args,
# start_date=days_ago(3), catchup=True, max_active_runs=3) as dag:
#     task_1 = DummyOperator(
#                 task_id='task_1',
#                 retry=3,
#                 retry_delay=timedelta(minutes=10)
#         )

#     task_2 = DummyOperator(
#                 task_id='task_2'
#         )

#     task_3 = DummyOperator(
#                 task_id='task_3'
#         )

# def _downloading_data(**kwargs):
#     print(kwargs)

def _downloading_data(my_param, ds, ti):
    print(my_param, ds)
    with open('/tmp/my_file.txt','w') as f:
        f.write("Prachi is cool")
    ti.xcom_push(key='my_key', value=43)
    # return 42 #automatically becomes xcom object

def _checking_data(ti):
    my_xcom = ti.xcom_pull(key='my_key', task_ids=['downloading_data'])
    print(my_xcom)

def _failure(context):
    print("On failure callback")
    print(context)

with DAG(dag_id='first_dag', schedule_interval="@daily", default_args=default_args,
start_date=days_ago(3), catchup=True) as dag:# max_active_runs=3
    
    downloading_data = PythonOperator(
        task_id = 'downloading_data',
        python_callable = _downloading_data,
        op_kwargs = {'my_param':111}
    )

    checking_data = PythonOperator(
        task_id='checking_data',
        python_callable=_checking_data
    )

    waiting_for_data = FileSensor(
        task_id='waiting_for_data',
        fs_conn_id='fs_default',
        filepath='my_file.txt'
        # poke_interval=15
    )

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 1',
        on_failure_callback=_failure
    )

    # downloading_data.set_downstream(waiting_for_data)
    # waiting_for_data.set_downstream(processing_data)

    # processing_data.set_upstream(waiting_for_data)
    # waiting_for_data.set_upstream(downloading_data)

    # downloading_data >> waiting_for_data >> processing_data
    # downloading_data >> [waiting_for_data, processing_data]
    chain(downloading_data, checking_data, waiting_for_data, processing_data)

    # cross_downstream([downloading_data,checking_data],[waiting_for_data, processing_data])
