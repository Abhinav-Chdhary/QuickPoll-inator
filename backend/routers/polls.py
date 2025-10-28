# routers/polls.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import List

# Import models
from models.mongo_models import (
    PollCreate,
    PollInDB,
    PollResponse,
    PyObjectId,
    PollLikeActionInDB,
    PollOptionCreate,
    PollOptionInDB,
    PollOptionResponse,
    PollVoteActionInDB,
)

# Import auth utilities
from utils.auth import decode_access_token

# We assume you have created these functions in 'utils/database.py'
from utils.database import (
    get_all_polls_from_db,
    get_poll_by_id_from_db,
    create_poll_in_db,
    update_poll_likes_in_db,
    get_like_action_from_db,
    create_like_action_in_db,
    delete_like_action_in_db,
    get_options_for_poll_from_db,
    create_poll_option_in_db,
    get_poll_option_by_id_from_db,
    update_poll_option_votes_in_db,
    get_vote_action_by_poll_from_db,
    create_vote_action_in_db,
    delete_vote_action_in_db,
)

router = APIRouter(prefix="/polls", tags=["polls"])

# Security scheme for protected routes
security = HTTPBearer()


# --- Helper Function to Get Current User ID ---
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Decodes the JWT token and returns the user_id.
    Raises HTTPException if the token is invalid or user_id is missing.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


# POLL OPTIONS
# Route to create a poll option
@router.post(
    "/{poll_id}/options",
    response_model=PollOptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_poll_option(
    poll_id: str,
    option_data: PollOptionCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Add an option to a poll.
    Only the creator of the poll can add options.
    """
    try:
        valid_poll_id = PyObjectId(poll_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Poll ID format"
        )

    # Check if the poll exists
    poll = await get_poll_by_id_from_db(valid_poll_id)
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found"
        )

    # Check if the user is the creator of the poll
    if poll["creator_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the poll creator can add options",
        )

    # Create the new poll option document
    option_doc = PollOptionInDB(
        poll_id=poll_id,  # Store the string ID
        text=option_data.text,
        votes=0,
        created_at=datetime.utcnow(),
    )
    option_dict = option_doc.model_dump(by_alias=True, exclude=["id"])

    # Insert into database
    result = await create_poll_option_in_db(option_dict)

    if result.inserted_id:
        # Fetch the new option to return it
        new_option = await get_poll_option_by_id_from_db(result.inserted_id)
        return new_option

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create poll option",
    )


# Route to vote on a poll option
@router.post("/{poll_id}/options/{option_id}/vote", response_model=PollOptionResponse)
async def toggle_poll_option_vote(
    poll_id: str,
    option_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Toggle a 'vote' on a poll option.
    This logic ensures one vote per user *per poll*.
    - If user votes for an option: vote is cast.
    - If user votes for the *same* option: vote is removed (un-voted).
    - If user votes for a *different* option: old vote is removed, new vote is cast.
    """
    try:
        valid_poll_id = PyObjectId(poll_id)
        valid_option_id = PyObjectId(option_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Poll or Option ID format",
        )

    # Check if the option exists and belongs to the correct poll
    option = await get_poll_option_by_id_from_db(valid_option_id)
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Poll option not found"
        )
    if option["poll_id"] != poll_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Option does not belong to this poll",
        )

    # Check if the user has an existing vote *on this poll*
    existing_vote = await get_vote_action_by_poll_from_db(
        user_id=user_id, poll_id=poll_id
    )

    if existing_vote:
        old_option_id_str = existing_vote["poll_option_id"]
        old_option_id_obj = existing_vote[
            "poll_option_id_obj"
        ]  # Using PyObjectId from helper

        # Delete the old vote action
        await delete_vote_action_in_db(existing_vote["_id"])

        # Decrement the old option's vote count
        await update_poll_option_votes_in_db(old_option_id_obj, -1)

        # 3c. Check if the user is un-voting (clicked the same option again)
        if old_option_id_str == option_id:
            # User un-voted. Fetch the updated option and return.
            updated_option = await get_poll_option_by_id_from_db(valid_option_id)
            return updated_option

    # If we are here, it's a new vote or a changed vote.
    # Create a new vote action
    vote_doc = PollVoteActionInDB(
        poll_id=poll_id,
        poll_option_id=option_id,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    vote_dict = vote_doc.model_dump(by_alias=True, exclude=["id"])
    await create_vote_action_in_db(vote_dict)

    # Increment the *new* option's vote count
    await update_poll_option_votes_in_db(valid_option_id, 1)

    # Fetch the newly updated option and return it
    final_option = await get_poll_option_by_id_from_db(valid_option_id)
    return final_option


# POLLS
# Route to fetch all polls
@router.get("/", response_model=List[PollResponse])
async def get_all_polls():
    """
    Retrieve all polls from the database.
    """
    polls_list = await get_all_polls_from_db()
    return polls_list


# Route to fetch poll by id
@router.get("/{poll_id}", response_model=PollResponse)
async def get_poll_by_id(poll_id: str):
    """
    Retrieve a single poll by its ID.
    """
    try:
        # Validate the ObjectId format
        valid_id = PyObjectId(poll_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Poll ID format"
        )

    poll = await get_poll_by_id_from_db(valid_id)

    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found"
        )

    # Fetch the options for this poll
    options_list = await get_options_for_poll_from_db(poll_id)

    # Add the options list to the poll dictionary
    poll["options"] = options_list

    # Return the combined dictionary.
    return poll


# Route to create a poll
@router.post(
    "/create", response_model=PollResponse, status_code=status.HTTP_201_CREATED
)
async def create_poll(
    poll_data: PollCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new poll. Requires authentication.

    - **text**: The poll question/text (min 5, max 280 characters).
    """
    # Create the PollInDB document
    poll_doc = PollInDB(
        text=poll_data.text,
        creator_id=user_id,
        created_at=datetime.utcnow(),
        likes=0,
    )

    # Convert to dict for database insertion, excluding 'id'
    poll_dict = poll_doc.model_dump(by_alias=True, exclude=["id"])

    # Insert into database
    result = await create_poll_in_db(poll_dict)

    if result.inserted_id:
        # Use the ID from the result to fetch the new poll
        new_poll = await get_poll_by_id_from_db(result.inserted_id)
        # Return the poll document, NOT the 'result' object
        return new_poll

    if not new_poll:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create poll",
        )

    return new_poll


# Route to toggle liking of a poll
@router.post("/{poll_id}/like", response_model=PollResponse)
async def toggle_poll_like(
    poll_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Toggle a 'like' on a poll.
    If the user has already liked the poll, it will be 'unliked'.
    If the user has not liked it, it will be 'liked'.
    Requires authentication.
    """
    try:
        # Validate the ObjectId format
        valid_poll_id = PyObjectId(poll_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Poll ID format"
        )

    # Check if the poll exists
    poll = await get_poll_by_id_from_db(valid_poll_id)
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found"
        )

    # Check if the user has already liked this poll
    existing_like = await get_like_action_from_db(user_id=user_id, poll_id=poll_id)

    update_result = None

    if existing_like:
        # UNLIKE: Delete the like action
        await delete_like_action_in_db(existing_like["_id"])

        # Decrement the poll's like count
        update_result = await update_poll_likes_in_db(valid_poll_id, -1)

    else:
        # LIKE: Create a new like action document
        like_doc = PollLikeActionInDB(
            poll_id=poll_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
        like_dict = like_doc.model_dump(by_alias=True, exclude=["id"])
        await create_like_action_in_db(like_dict)

        # 4b. Increment the poll's like count
        update_result = await update_poll_likes_in_db(valid_poll_id, 1)

    # Check if the update operation actually modified anything
    if not update_result or update_result.modified_count == 0:
        # This might happen in a race condition, but we'll fetch the poll anyway
        pass

    # Fetch the updated poll to return the latest state
    updated_poll_document = await get_poll_by_id_from_db(valid_poll_id)

    if not updated_poll_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found after like update",
        )

    return updated_poll_document
