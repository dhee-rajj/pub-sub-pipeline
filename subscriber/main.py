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
            # Parse the data string into a dictionary
            data_dict = json.loads(data)
            message = data_dict.get("message")
            topic = body.get("topic")
            if message is None or topic is None:
                logger.warning(
                    "Received message with missing topic or message")
            else:
                logger.info(f"Received message on {topic} topic: {message}")
                if topic == "create-product-topic":
                    logger.info(f"Processing product message: {message}")
                elif topic == "get-products-topic":
                    logger.info(f"Processing get-products message: {message}")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON data")
    else:
        logger.warning("Received message with missing data field")
    return {}  # Return an empty JSON object to indicate success


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    return [
        {"pubsubname": "pubsub", "topic": "create-product-topic", "route": "/subscribe/"},
        {"pubsubname": "pubsub", "topic": "get-products-topic", "route": "/subscribe/"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
