from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/dapr/subscribe")
async def subscribe_message(request: Request):
    event = await request.json()
    message = event.get('data', {}).get('message')
    if message:
        print(f"Received message: {message}")
        return {"status": "Message received"}, 204
    else:
        return {"status": "Message not found"}, 422

@app.get("/dapr/subscribe")
async def get_subscribe():
    return [
        {
            "pubsubname": "pubsub",
            "topic": "test-topic",
            "route": "/dapr/subscribe"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)