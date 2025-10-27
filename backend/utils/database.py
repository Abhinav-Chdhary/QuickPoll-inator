# utils/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from dbconn import get_database


# USER
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

# POLL
# Get all polls from the database
async def get_all_polls_from_db():
    """Get all polls from the database."""
    db = get_database()
    polls_collection = db["polls"]
    polls = await polls_collection.find().to_list(100)
    return polls

# Get a poll from the database by id
async def get_poll_by_id_from_db(poll_id: str):
    """Get a poll from the database by id."""
    db = get_database()
    polls_collection = db["polls"]
    poll = await polls_collection.find_one({"_id": poll_id})
    return poll

# Insert a new poll into the database
async def create_poll_in_db(poll_data: dict):
    """Insert a new poll into the database."""
    db = get_database()
    polls_collection = db["polls"]
    result = await polls_collection.insert_one(poll_data)
    print("\n--- POLL CREATED ---")
    print(result)
    print("-------------------\n")
    return result

