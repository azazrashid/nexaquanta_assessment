from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    full_name: str = Field(None, min_length=1, max_length=255,
                           description="User's full name")


class UserUpdate(BaseModel):
    password: str | None = None
    full_name: str | None = None
    is_active: int | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str