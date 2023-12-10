from uuid import uuid4

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, func

from app.db import BaseModel
from app.models.mixins import ModelMixin


__all__ = ("Post",)


class Post(ModelMixin, BaseModel):
    __tablename__ = "post"

    id = Column(String(36), default=lambda: str(uuid4()), primary_key=True)
    author = Column(ForeignKey("userprofile.id", ondelete="CASCADE"))
    title = Column(String(64), nullable=False, default="")
    content = Column(String(1024), nullable=False, default="")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    repost_on = Column(ForeignKey("post.id", ondelete="SET NULL"))
    is_private = Column(Boolean, default=False)
