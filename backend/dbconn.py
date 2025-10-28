# dbconn.py
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from typing import Optional

# Load env variables
load_dotenv()

# --- Configuration ---
# For a local MongoDB, this might be: "mongodb://localhost:27017/"
ATLAS_URI: Optional[str] = os.environ.get("MONGO_URI")
DB_NAME: Optional[str] = os.environ.get("DB_NAME")

if not ATLAS_URI:
    raise RuntimeError("MONGO_URI environment variable is not set")


# Shared MongoClient instance for the app (Initialized to None)
client = None
db = None


# Function to initialize and test the MongoDB connection
def startup_client():
    """Initializes and tests the MongoDB connection."""
    global client, db
    try:
        # Create a AsyncIOMotorClient instance (async version)
        client = AsyncIOMotorClient(ATLAS_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]

        # The 'ping' command tests the connection
        client.admin.command("ping")
        print("✅ Successfully connected to MongoDB.")

    # Catch any other unexpected error
    except Exception as e:
        print(f"❌ An unexpected error occurred during MongoDB startup: {e}")
        raise ConnectionError(
            "An unexpected error occurred during database connection."
        ) from e


def get_database():
    """Return the database instance."""
    if db is None:
        raise RuntimeError("Database not initialized. Call startup_client() first.")
    return db


# Function to get the MongoDB client instance
def get_client():
    """Returns the globally available MongoClient instance."""
    if client is None:
        # This shouldn't happen if startup_client runs successfully
        raise RuntimeError("MongoDB client is not initialized.")
    return client


# Function to close the MongoDB client instance
def close_client():
    """Closes the globally available MongoClient connection."""
    if client:
        client.close()
        print("🔌 MongoDB connection closed.")
