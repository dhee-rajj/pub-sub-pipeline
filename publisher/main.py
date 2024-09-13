import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.clients import DaprClient
# from pipeline.pipeline import add_products_to_db
import logging
from database.tursodb import insert_product
import modal

logger = logging.getLogger("uvicorn")


def publish_message(message: str):
    payload = {"message": message}
    logger.info(f"Publishing to test-db with payload: {payload}")
    
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="pubsub",
            topic_name="test-db",
            data=json.dumps(payload),
        )
    logger.info(f"Publish result: Success")
    
    return {"status": "Message published", "message": message}

# Initialize FastAPI app
app = FastAPI()

# Define a Pydantic model for the product
class Product(BaseModel):
    name: str
    price: float

@app.post("/create_product")
async def create_product(product: Product):
    try:
        # Add product to the database
        insert_product(product.name, product.price)
        
        # Create a message to publish
        message = f"Product added: {product.name} with price {product.price}"
        
        # Publish the message using the existing function
        result = publish_message(message)
        
        return result
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)