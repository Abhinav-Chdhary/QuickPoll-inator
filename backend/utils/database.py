# utils/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from dbconn import get_database
from models.mongo_models import PyObjectId


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
    return result


# Update a poll's like count
async def update_poll_likes_in_db(poll_id: str, increment: int):
    """Update a poll's like count."""
    db = get_database()
    polls_collection = db["polls"]
    result = await polls_collection.update_one(
        {"_id": poll_id}, {"$inc": {"likes": increment}}
    )
    return result


# POLL LIKE ACTION
async def get_like_action_from_db(user_id: str, poll_id: str):
    """Find if a specific user has liked a specific poll."""
    db = get_database()
    poll_like_actions_collection = db["poll_like_actions"]
    like_action = await poll_like_actions_collection.find_one(
        {"user_id": user_id, "poll_id": poll_id}
    )
    return like_action


# Insert a new poll like action into the database
async def create_like_action_in_db(like_data: dict):
    """Insert a new poll like action into the database."""
    db = get_database()
    poll_like_actions_collection = db["poll_like_actions"]
    result = await poll_like_actions_collection.insert_one(like_data)
    return result


# Delete a poll like action from the database by its _id
async def delete_like_action_in_db(like_id: PyObjectId):
    """Delete a poll like action from the database by its _id."""
    db = get_database()
    poll_like_actions_collection = db["poll_like_actions"]
    result = await poll_like_actions_collection.delete_one({"_id": like_id})
    return result


# POLL OPTION
async def create_poll_option_in_db(option_data: dict):
    """Insert a new poll option into the database."""
    db = get_database()
    poll_options_collection = db["poll_options"]
    result = await poll_options_collection.insert_one(option_data)
    return result


async def get_poll_option_by_id_from_db(option_id: PyObjectId):
    """Get a poll option from the database by id."""
    db = get_database()
    poll_options_collection = db["poll_options"]
    option = await poll_options_collection.find_one({"_id": option_id})
    return option


async def update_poll_option_votes_in_db(option_id: PyObjectId, increment: int):
    """Update a poll option's vote count."""
    db = get_database()
    poll_options_collection = db["poll_options"]
    result = await poll_options_collection.update_one(
        {"_id": option_id}, {"$inc": {"votes": increment}}
    )
    return result


# POLL VOTE ACTION
async def get_vote_action_by_poll_from_db(user_id: str, poll_id: str):
    """
    Find if a user has already voted on *any* option in this poll.
    Returns the single vote action document if it exists.
    """
    db = get_database()
    poll_vote_actions_collection = db["poll_vote_actions"]
    vote_action = await poll_vote_actions_collection.find_one(
        {"user_id": user_id, "poll_id": poll_id}
    )
    # Also add the PyObjectId version for convenience in the router
    if vote_action:
        vote_action["poll_option_id_obj"] = PyObjectId(vote_action["poll_option_id"])
    return vote_action


async def create_vote_action_in_db(vote_data: dict):
    """Insert a new poll vote action into the database."""
    db = get_database()
    poll_vote_actions_collection = db["poll_vote_actions"]
    result = await poll_vote_actions_collection.insert_one(vote_data)
    return result


async def delete_vote_action_in_db(vote_id: PyObjectId):
    """Delete a poll vote action from the database by its _id."""
    db = get_database()
    poll_vote_actions_collection = db["poll_vote_actions"]
    result = await poll_vote_actions_collection.delete_one({"_id": vote_id})
    return result
