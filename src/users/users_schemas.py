from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: EmailStr
    phone_number: str | None = Field(None, max_length=20)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8)
    email: EmailStr | None = None
    phone_number: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    phone_number: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

