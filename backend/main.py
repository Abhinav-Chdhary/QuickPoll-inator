# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Internal imports
from dbconn import startup_client, close_client
from routers import users, polls, websocket

# Load env variables
load_dotenv()

# FastAPI App Initialization
app = FastAPI(title="QuickPoll API")

# Include routers
app.include_router(users.router)
app.include_router(polls.router)
app.include_router(websocket.router)

# Get frontend url from env
FRONTEND_URL = os.environ.get("FRONTEND_URL")

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MongoDB connection events
@app.on_event("startup")
async def startup_event():
    """FastAPI startup event handler."""
    # Initialize and test the MongoDB connection
    startup_client()


@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI shutdown event handler."""
    # Close the MongoDB connection
    close_client()


# Example Route
@app.get("/")
async def root():
    return {"message": "Hello from quick poll-inator"}
