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
)

# Import auth utilities
from utils.auth import decode_access_token

# We assume you have created these functions in 'utils/database.py'
from utils.database import (
    get_all_polls_from_db,
    get_poll_by_id_from_db,
    create_poll_in_db,
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
    return poll


# Route to create a poll
@router.post("/create", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
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


# # Route to toggle liking of a poll
# @router.post("/{poll_id}/like", response_model=PollResponse)
# async def toggle_poll_like(
#     poll_id: str,
#     user_id: str = Depends(get_current_user_id),
# ):
#     """
#     Toggle a 'like' on a poll.
#     If the user has already liked the poll, it will be 'unliked'.
#     If the user has not liked it, it will be 'liked'.
#     Requires authentication.
#     """
#     try:
#         # Validate the ObjectId format
#         valid_poll_id = PyObjectId(poll_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Poll ID format"
#         )

#     # 1. Check if the poll exists
#     poll = await get_poll_by_id_from_db(valid_poll_id)
#     if not poll:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found"
#         )

#     # 2. Check if the user has already liked this poll
#     # We use poll_id (str) and user_id (str) as defined in PollLikeActionInDB
#     existing_like = await get_like_action_from_db(user_id=user_id, poll_id=poll_id)

#     if existing_like:
#         # --- UNLIKE ---
#         # 3a. Delete the like action
#         await delete_like_action_in_db(existing_like["_id"])

#         # 4a. Decrement the poll's like count
#         updated_poll = await update_poll_likes_in_db(valid_poll_id, -1)

#     else:
#         # --- LIKE ---
#         # 3b. Create a new like action document
#         like_doc = PollLikeActionInDB(
#             poll_id=poll_id,
#             user_id=user_id,
#             created_at=datetime.utcnow(),
#         )
#         like_dict = like_doc.model_dump(by_alias=True, exclude=["id"])
#         await create_like_action_in_db(like_dict)

#         # 4b. Increment the poll's like count
#         updated_poll = await update_poll_likes_in_db(valid_poll_id, 1)

#     if not updated_poll:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update poll like count",
#         )

#     return updated_poll
