# utils/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from dbconn import get_database

# Get a user from the database by email
async def get_user_by_email(email: str):
    """Get a user from the database by email."""
    db = get_database()
    users_collection = db["users"]
    user = await users_collection.find_one({"email_id": email})
    return user

# Insert a new user into the database
async def create_user_in_db(user_data: dict):
    """Insert a new user into the database."""
    db = get_database()
    users_collection = db["users"]
    result = await users_collection.insert_one(user_data)
    return result
