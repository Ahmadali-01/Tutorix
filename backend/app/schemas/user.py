import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    roles: Optional[List[str]] = []


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"