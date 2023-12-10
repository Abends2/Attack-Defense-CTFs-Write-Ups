from uuid import uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db import BaseModel
from app.models.mixins import ModelMixin


__all__ = ("Subscribe",)


class Subscribe(ModelMixin, BaseModel):
    __tablename__ = "subscribe"

    id = Column(String(36), default=lambda: str(uuid4()), primary_key=True)
    subscriber = Column(ForeignKey("userprofile.id", ondelete="CASCADE"))
    subscribe_profile = Column(ForeignKey("userprofile.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
