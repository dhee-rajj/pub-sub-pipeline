from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class PublishRequest(BaseModel):
    topic: str
    message: str

@app.post("/publish/")
async def publish_message(request: PublishRequest):
    dapr_url = f"http://localhost:3500/v1.0/publish/pubsub/{request.topic}"
    payload = {"message": request.message}
    response = requests.post(dapr_url, json=payload)
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"status": "Message published"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)