from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from publisher.main import publish_message
from pipeline.pipeline import data_pipeline
from dagster import execute_pipeline

app = FastAPI()
logger = logging.getLogger("uvicorn")

class PublishRequest(BaseModel):
    message: str

@app.post("/publish")
async def publish_message_endpoint(request: PublishRequest):
    try:
        response = publish_message(request.message)
        return response
    except Exception as e:
        logger.error(f"Error publishing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/run-pipeline")
def run_pipeline():
    result = execute_pipeline(data_pipeline)
    if result.success:
        return {"status": "Pipeline executed successfully"}
    else:
        return {"status": "Pipeline execution failed", "errors": result.errors}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)