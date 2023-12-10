from datetime import datetime

from pydantic import UUID4, BaseModel, field_validator


__all__ = (
    "UserCreate",
    "UserGet",
    "TokenBase",
)


class UserBase(BaseModel):
    username: str
    fullname: str
    bio: str


class UserCreate(UserBase):
    password: str


class UserGet(UserBase):
    id: UUID4
    avatar: str | None


class TokenBase(BaseModel):
    """Return response data"""

    access_token: UUID4
    expires: datetime
    token_type: str | None = "bearer"

    class Config:
        populate_by_name = True

    @staticmethod
    @field_validator("token")
    def hexlify_token(value):
        """Convert UUID to pure hex string"""
        return value.hex
