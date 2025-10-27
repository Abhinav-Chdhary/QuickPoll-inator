# models/mongo_models.py
from pydantic import BaseModel, Field, EmailStr, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId


# MongoDB Utility Types
class PyObjectId(ObjectId):
    """Custom type for Pydantic v2 to handle MongoDB's ObjectId."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}


class MongoBaseModel(BaseModel):
    """Base model to handle MongoDB's default _id field."""

    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }


# User Schema
class UserCreate(BaseModel):
    """Data model for creating a new User."""

    name: str = Field(..., min_length=2)
    email_id: EmailStr
    password: str = Field(..., min_length=6)


class UserInDB(MongoBaseModel):
    """Data model for a User document stored in MongoDB."""

    name: str
    email_id: EmailStr
    password: str  # Hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(MongoBaseModel):
    """Data model for API responses (excludes password)."""

    name: str
    email_id: EmailStr
    created_at: datetime


class UserLogin(BaseModel):
    """Data model for user login."""

    email_id: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Data model for token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Poll Schema
class PollCreate(BaseModel):
    """Data model for creating a new Poll."""

    text: str = Field(..., min_length=3, max_length=300)


class PollInDB(MongoBaseModel):
    """Data model for a Poll document stored in MongoDB."""

    text: str
    likes: int = Field(default=0, ge=0)
    creator_id: str  # ID of the User who created the poll
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PollResponse(PollInDB):
    """Data model for API responses."""

    pass


# Poll Option Schema
class PollOptionCreate(BaseModel):
    """Data model for creating a new Poll Option."""

    text: str = Field(..., min_length=1, max_length=100)


class PollOptionInDB(MongoBaseModel):
    """Data model for a Poll Option document stored in MongoDB."""

    poll_id: str  # ID of the Poll this option belongs to
    text: str
    votes: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PollOptionResponse(PollOptionInDB):
    """Data model for API responses."""

    pass


# Poll Like Action Schema
class PollLikeActionInDB(MongoBaseModel):
    """Tracks a single 'like' action by a user on a poll."""

    poll_id: str
    user_id: str  # The ID of the user who liked the poll
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Poll Vote Action Schema
class PollVoteActionInDB(MongoBaseModel):
    """Tracks a single 'vote' action by a user on a poll option."""

    poll_id: str
    poll_option_id: str
    user_id: str  # The ID of the user who voted
    created_at: datetime = Field(default_factory=datetime.utcnow)
