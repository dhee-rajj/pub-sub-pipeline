from pydantic import BaseModel
from dagster import execute_job, DagsterInstance, reconstructable, DagsterInvalidInvocationError, DagsterUserCodeExecutionError
from collect_task.pipeline import my_job 
from fastapi import FastAPI, HTTPException
from collect_task.modal_pipeline import my_pipeline
from typing import Any
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class Task(BaseModel):
    name: str

class JobResponse(BaseModel):
    status: str

@app.post("/collect_tasks", response_model=JobResponse)
async def collect_tasks(task: Task) -> JobResponse:
    try:
        if task.name == "csv":
            # Load and process data
            logger.info("Data loaded and processed successfully.")

            # Ensure DAGSTER_HOME is set
            dagster_home = os.getenv("DAGSTER_HOME")
            if not dagster_home:
                raise HTTPException(status_code=500, detail="The environment variable $DAGSTER_HOME is not set. Please set it to a valid directory.")

            # Create an instance of DagsterInstance
            instance = DagsterInstance.get()

            # Convert the job to a ReconstructableJob
            reconstructable_job = reconstructable(my_job)

            # Trigger the Dagster job
            result = execute_job(job=reconstructable_job, instance=instance)

            if not result.success:
                # Inspect individual op failures and provide more details
                error_messages = [str(e) for e in result.failure_data.errors]
                raise HTTPException(status_code=500, detail="Job execution failed:\n" + "\n".join(error_messages))
            return JobResponse(status="Job executed successfully")
        else:
            raise HTTPException(status_code=400, detail="Invalid task name")
    except (DagsterInvalidInvocationError, DagsterUserCodeExecutionError) as e:
        logger.error(f"Dagster error: {e}")
        raise HTTPException(status_code=500, detail=f"Dagster error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    
@app.post("/run_pipeline", response_model=JobResponse)
async def run_pipeline() -> JobResponse:
    try:
        # Ensure DAGSTER_HOME is set
        dagster_home = os.getenv("DAGSTER_HOME")
        if not dagster_home:
            raise HTTPException(status_code=500, detail="The environment variable $DAGSTER_HOME is not set. Please set it to a valid directory.")

        # Create an instance of DagsterInstance
        instance = DagsterInstance.get()

        # Convert the job to a ReconstructableJob
        reconstructable_job = reconstructable(my_pipeline)

        # Trigger the Dagster job
        result = execute_job(job=reconstructable_job, instance=instance)

        if not result.success:
            # Inspect individual op failures and provide more details
            error_messages = [str(e) for e in result.failure_data.errors]
            raise HTTPException(status_code=500, detail="Job execution failed:\n" + "\n".join(error_messages))
        return JobResponse(status="Pipeline executed successfully")
    except (DagsterInvalidInvocationError, DagsterUserCodeExecutionError) as e:
        logger.error(f"Dagster error: {e}")
        raise HTTPException(status_code=500, detail=f"Dagster error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")