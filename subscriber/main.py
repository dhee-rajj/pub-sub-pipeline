from fastapi import FastAPI, Request
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/subscribe/")
async def subscribe_message(request: Request):
    body = await request.json()
    data = body.get("data")
    if data:
        try:
            data_dict = json.loads(data)  # Parse the data string into a dictionary
            message = data_dict.get("message")
            if message is None:
                logger.warning("Received message with missing topic or message")
            else:
                logger.info(f"Received message on test-topic message: {message}")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON data")
    else:
        logger.warning("Received message with missing data field")
    return {}  # Return an empty JSON object to indicate success

@app.get("/dapr/subscribe")
async def dapr_subscribe():
    return [{"pubsubname": "pubsub", "topic": "test-topic", "route": "/subscribe/"}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)