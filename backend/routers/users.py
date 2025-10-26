# routers/users.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

# Import your models
from models.mongo_models import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
)

# Import auth utilities
from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from utils.database import get_user_by_email, create_user_in_db
from datetime import timedelta

router = APIRouter(prefix="/user", tags=["users"])

# Security scheme for protected routes
security = HTTPBearer()


# Route to register a user
@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate):
    """
    Register a new user.

    - **name**: User's full name (min 2 characters)
    - **email_id**: Valid email address
    - **password**: Password (min 8 characters)

    Returns an access token and user information.
    """

    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create user document
    user_dict = {
        "name": user_data.name,
        "email_id": user_data.email_id,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
    }

    # Insert user into database
    await create_user_in_db(user_dict)

    # Retrieve the created user
    created_user = await get_user_by_email(user_data.email_id)

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user_data.email_id, "user_id": str(created_user["_id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Prepare user response (exclude password)
    user_response = UserResponse(
        id=created_user["_id"],
        name=created_user["name"],
        email_id=created_user["email_id"],
        created_at=created_user["created_at"],
    )

    return TokenResponse(
        access_token=access_token, token_type="bearer", user=user_response
    )


# Route to login a user
@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login an existing user.

    - **email_id**: User's email address
    - **password**: User's password

    Returns an access token and user information.
    """

    # Find user by email
    user = await get_user_by_email(credentials.email_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user["email_id"], "user_id": str(user["_id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Prepare user response (exclude password)
    user_response = UserResponse(
        id=user["_id"],
        name=user["name"],
        email_id=user["email_id"],
        created_at=user["created_at"],
    )

    return TokenResponse(
        access_token=access_token, token_type="bearer", user=user_response
    )


# Route to get current user
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Get current authenticated user information.

    Requires Bearer token in Authorization header.
    """

    # Decode the JWT token
    token = credentials.credentials
    payload = decode_access_token(token)

    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Get user from database
    user = await get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return UserResponse(
        id=user["_id"],
        name=user["name"],
        email_id=user["email_id"],
        created_at=user["created_at"],
    )
