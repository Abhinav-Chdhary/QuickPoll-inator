# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

# Internal imports
from dbconn import startup_client, close_client
from routers import users, polls, websocket

# Load env variables
load_dotenv()


# Define the Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage startup and shutdown events.
    """
    print("Application startup...")
    # Initialize and test the MongoDB connection
    startup_client()
    try:
        yield
    finally:
        # Close the MongoDB connection
        print("Application shutdown...")
        close_client()


# FastAPI App Initialization
app = FastAPI(title="QuickPoll API", lifespan=lifespan)

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


# Example Route
@app.get("/")
async def root():
    return {"message": "Hello from quick poll-inator"}
