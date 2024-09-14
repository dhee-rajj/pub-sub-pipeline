import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.clients import DaprClient
import logging
from database.tursodb import insert_product, get_connection

logger = logging.getLogger("uvicorn")


def publish_message(message: str, topic_name: str):
    payload = {"message": message}
    logger.info(f"Publishing to test-db with payload: {payload}")
    
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="pubsub",
            topic_name=topic_name,
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
        result = publish_message(message, "create-product-topic")
        
        return result
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")


@app.post("/get_products")
async def get_products():
    try:
        conn = get_connection()
        results = conn.execute("SELECT * FROM products").fetchall()
        
        for row in results:
            product = {
                "name": row[0],
                "price": row[1]
            }
            message = f"Product: {product['name']} with price {product['price']}"
            
            # Publish the message using the existing function
            publish_message(message, "get-products-topic")
        
        return {"status": "Products Fetched"}
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get products")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)