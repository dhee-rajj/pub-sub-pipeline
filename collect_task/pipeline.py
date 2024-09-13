from dagster import op, job
from collect_task.dkdb import load_and_process_data  # Import the function from dkdb.py


@op
def load_and_process_data_op(context):
    load_and_process_data()

@job
def my_job():
    load_and_process_data_op()