from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from dapr.clients import DaprClient
import logging
from database.tursodb import insert_product, get_connection
from typing import List, Dict

logger = logging.getLogger("uvicorn")

class Payload(BaseModel):
    message: str

def publish_message(message: str, topic_name: str) -> Dict[str, str]:
    payload = Payload(message=message)
    logger.info(f"Publishing to test-db with payload: {payload.model_dump_json()}")
    
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="pubsub",
            topic_name=topic_name,
            data=payload.model_dump_json(),
        )
    logger.info(f"Publish result: Success")
    
    return {"status": "Message published", "message": message}

# Initialize FastAPI app
app = FastAPI()

# Define a Pydantic model for the product
class Product(BaseModel):
    name: str
    price: float

# Define a Pydantic model for the response
class ProductResponse(BaseModel):
    message: str

class ProductsListResponse(BaseModel):
    products: List[Product]

@app.post("/create_product", response_model=ProductResponse)
async def create_product(product: Product) -> ProductResponse:
    try:
        # Add product to the database without the id
        insert_product(product.name, product.price)
        
        # Create a message to publish
        message = f"Product added: {product.name} with price {product.price}"
        
        # Publish the message using the existing function
        result = publish_message(message, "create-product-topic")
        
        return ProductResponse(message=result["message"])
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@app.post("/get_products", response_model=ProductsListResponse)
async def get_products() -> ProductsListResponse:
    try:
        conn = get_connection()
        results = conn.execute("SELECT * FROM products").fetchall()
        
        products: List[Product] = []
        for row in results:
            try:
                # Ensure correct types for the Product model
                product = Product(id=int(row[0]), name=str(row[1]), price=float(row[2]))
                products.append(product)
                
                message = f"Product: {product.name} with price {product.price}"
                
                # Publish the message using the existing function
                publish_message(message, "get-products-topic")
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing product data: {e}")
                continue
        
        return ProductsListResponse(products=products)
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get products")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)