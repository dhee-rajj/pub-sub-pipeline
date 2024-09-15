from dagster import op, job, OpExecutionContext
from collect_task.dkdb import load_and_process_data  # Import the function from dkdb.py

@op
def load_and_process_data_op(context: OpExecutionContext) -> None:
    load_and_process_data()

@job
def my_job() -> None:
    load_and_process_data_op()