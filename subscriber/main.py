from pydantic import BaseModel, field_validator
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class MessagePayload(BaseModel):
    message: str

class SubscribeRequest(BaseModel):
    data: MessagePayload
    topic: str

    @field_validator('data', mode='before')
    def deserialize_data(cls, value: Union[str, MessagePayload]) -> MessagePayload:
        if isinstance(value, str):
            return MessagePayload.model_validate_json(value)
        return value

class DaprSubscription(BaseModel):
    pubsubname: str
    topic: str
    route: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.post("/subscribe/", response_model=Dict[str, Any])
async def subscribe_message(subscribe_request: SubscribeRequest) -> Dict[str, Any]:
    message = subscribe_request.data.message
    topic = subscribe_request.topic
    logger.info(f"Received message on {topic} topic: {message}")
    if topic == "create-product-topic":
        logger.info(f"Processing product message: {message}")
    elif topic == "get-products-topic":
        logger.info(f"Processing get-products message: {message}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported topic")
    return {}  # Return an empty JSON object to indicate success

@app.get("/dapr/subscribe", response_model=List[DaprSubscription])
async def dapr_subscribe() -> List[DaprSubscription]:
    return [
        {"pubsubname": "pubsub", "topic": "create-product-topic", "route": "/subscribe/"},
        {"pubsubname": "pubsub", "topic": "get-products-topic", "route": "/subscribe/"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)