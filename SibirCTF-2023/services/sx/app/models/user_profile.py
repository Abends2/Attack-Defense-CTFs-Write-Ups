from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func

from app.db import BaseModel
from app.models.mixins import ModelMixin


__all__ = (
    "UserProfile",
    "Token",
)


class UserProfile(ModelMixin, BaseModel):
    __tablename__ = "userprofile"

    id = Column(String(36), default=lambda: str(uuid4()), primary_key=True)
    username = Column(String(128), unique=True)
    fullname = Column(String(256))
    bio = Column(String(1024))
    password = Column(String(256))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    avatar = Column(String(128), nullable=True)


class Token(ModelMixin, BaseModel):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True)
    access_token = Column(String(36), unique=True)
    expires = Column(DateTime())
    user_id = Column(ForeignKey("userprofile.id", ondelete="CASCADE"))
