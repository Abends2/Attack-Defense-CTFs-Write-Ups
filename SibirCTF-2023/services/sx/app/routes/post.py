from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, update

from app.db import execute_command
from app.schemas import PostCreate, PostEdit, PostGet
from app.models import Post, Subscribe
from app.utils.auth import get_current_user


router = APIRouter(prefix="/posts", tags=["Post"])


@router.post("")
async def create_post(post: PostCreate, current_user=Depends(get_current_user)):
    if post.repost_on and not await Post.get(id=post.repost_on):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Such repost not found (parameter 'repost_on')",
        )

    values = post.model_dump() | {"author": current_user.id}
    query = insert(Post).values(**values).returning(Post)
    post = list((await execute_command(query, commit_after_execute=True)).scalars())[0]
    return PostGet(**post.to_dict())


@router.get("/{post_id}")
async def get_post(post_id: str, current_user=Depends(get_current_user)) -> PostGet:
    post = await Post.get(id=post_id)

    if post.is_private and post.author != current_user.id:
        if not await Subscribe.get(
            subscriber=post.author, subscribe_profile=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permissions to read a private post",
            )

    return PostGet(**post.to_dict())


@router.get("/user/{user_id}")
async def get_user_posts(
    user_id: str, current_user=Depends(get_current_user)
) -> list[PostGet]:
    if await Subscribe.get(subscriber=user_id, subscribe_profile=current_user.id):
        posts = await Post.get_all(author=user_id)
    else:
        posts = await Post.get_all(author=user_id, is_private=False)
    return [PostGet(**post.to_dict()) for post in posts]


@router.patch("/{post_id}")
async def patch_post(
    post_id: str, post_edit: PostEdit, current_user=Depends(get_current_user)
):
    post = await Post.get(id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if str(post.author) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Edition this post is not permitted to you!",
        )

    query = (
        update(Post)
        .where(Post.id == post_id)
        .values(**post_edit.model_dump(exclude_unset=True))
        .returning(Post)
    )
    post = list((await execute_command(query, commit_after_execute=True)).scalars())[0]
    return PostGet(**post.to_dict())
