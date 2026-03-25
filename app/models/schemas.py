from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ConnectedAccountOut(BaseModel):
    id: uuid.UUID
    platform: str
    platform_username: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DigestOut(BaseModel):
    id: uuid.UUID
    date: datetime
    summary: Optional[str]
    sentiment: Optional[str]
    total_comments: Optional[int]
    top_topics: Optional[str]
    platforms_included: Optional[str]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

class CommentOut(BaseModel):
    id: uuid.UUID
    platform: str
    author: Optional[str]
    content: Optional[str]
    sentiment: Optional[str]
    topic: Optional[str]
    fetched_at: datetime

    class Config:
        from_attributes = True