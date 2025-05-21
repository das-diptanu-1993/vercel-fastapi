from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/api/health_check")
async def health_check():
    return {"status": "ok", \
            "message": "Welcome to the FastAPI application!"}

@app.get("/api/get_image")
async def get_image():
    return {"image": "https://plus.unsplash.com/premium_photo-1747504296849-d477136528ed?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxmZWF0dXJlZC1waG90b3MtZmVlZHwyNXx8fGVufDB8fHx8fA%3D%3D"}

