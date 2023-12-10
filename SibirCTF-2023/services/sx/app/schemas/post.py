from datetime import datetime

from pydantic import UUID4, BaseModel


__all__ = (
    "PostCreate",
    "PostEdit",
    "PostGet",
)


class PostBase(BaseModel):
    title: str
    content: str
    is_private: bool = False


class PostCreate(PostBase):
    repost_on: str | None = None


class PostEdit(PostBase):
    title: str | None = None
    content: str | None = None


class PostGet(PostBase):
    id: UUID4
    author: UUID4
    repost_on: UUID4 | None = None
    created_at: datetime
    updated_at: datetime | None = None
