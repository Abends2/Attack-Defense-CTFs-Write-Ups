from fastapi import APIRouter, Depends, HTTPException, status

from app.managers import PostManager
from app.schemas import PostGet
from app.utils.auth import get_current_user


router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("/{feed_type}")
async def get_feed(
    feed_type: str, current_user=Depends(get_current_user)
) -> list[PostGet]:
    """Get feed

    feed_type:
    - *others* - get posts that could be interesting for you
    - *my* - get my posts
    """
    func = getattr(PostManager, feed_type, None)
    if func is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"feed_type {feed_type} is not allowed!",
        )

    posts = await func(current_user.id)
    return [PostGet(**post.to_dict()) for post in posts]
