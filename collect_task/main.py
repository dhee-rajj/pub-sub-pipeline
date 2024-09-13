from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dagster import execute_job, DagsterInstance, reconstructable, DagsterInvalidInvocationError, DagsterUserCodeExecutionError
from collect_task.pipeline import my_job 
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class Task(BaseModel):
    name: str

@app.post("/collect_tasks")
async def collect_tasks(task: Task):
    try:
        if task.name == "csv":
            # Load and process data
            logger.info("Data loaded and processed successfully.")

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
            return {"status": "Job executed successfully"}

    except DagsterInvalidInvocationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid job invocation: {str(e)}")
    except DagsterUserCodeExecutionError as e:
        raise HTTPException(status_code=500, detail=f"Job execution error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")