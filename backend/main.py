# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from dbconn import startup_client, close_client
from routers import users, polls, websocket

# FastAPI App Initialization
app = FastAPI(title="QuickPoll API")

# Include routers
app.include_router(users.router)
app.include_router(polls.router)
app.include_router(websocket.router)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
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
