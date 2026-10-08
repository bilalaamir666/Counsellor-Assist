from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


UserRole = Literal["admin", "counsellor"]


class User(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password_hash: str
    role: UserRole = "counsellor"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime