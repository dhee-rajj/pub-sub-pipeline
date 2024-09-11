import json
from dapr.clients import DaprClient
import logging

logger = logging.getLogger("uvicorn")

def publish_message(message: str):
    payload = {"message": message}
    logger.info(f"Publishing to test-topic with payload: {payload}")
    
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="pubsub",
            topic_name="test-topic",
            data=json.dumps(payload),
        )
    logger.info(f"Publish result: Success")
    
    return {"status": "Message published", "message": message}