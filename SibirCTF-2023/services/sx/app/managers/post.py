from sqlalchemy import or_
from sqlalchemy.future import select

from app.db import execute_command
from app.models import Post, Subscribe, UserProfile
from app.configs import RESPONSE_ITEMS_LIMIT

__all__ = ("PostManager",)


class PostManager:
    __get_all = Post.get_all

    @classmethod
    async def others(cls, current_user_id: str):
        # fmt: off
        your_subscribers = (
            select(UserProfile.id)
            .join(Subscribe, UserProfile.id == Subscribe.subscriber)
            .where(Subscribe.subscribe_profile == current_user_id)
        )

        query = (
            select(Post)
            .join(Subscribe, Post.author == Subscribe.subscribe_profile)
            .where(Subscribe.subscriber == current_user_id)
            .where(
                or_(
                    Post.is_private == False,
                    Post.author.in_(your_subscribers)
                )
            )
            .order_by(Post.created_at.desc())
            .limit(RESPONSE_ITEMS_LIMIT)
        )
        return list((await execute_command(query)).scalars())

    @classmethod
    async def my(cls, current_user_id: str):
        return await cls.__get_all(author=current_user_id)
