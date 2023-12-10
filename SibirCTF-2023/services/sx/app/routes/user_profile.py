from uuid import uuid4

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

from app.configs import AVATARS_DIR, MAX_AVATAR_SIZE
from app.schemas import UserCreate, UserGet
from app.models import UserProfile
from app.db import execute_command
from app.utils.auth import get_current_user


router = APIRouter(prefix="/users", tags=["User"])


@router.post("")
async def create_user(user: UserCreate) -> UserGet:
    existent_user = await UserProfile.get(username=user.username)
    if existent_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user.username} already registered",
        )

    query = insert(UserProfile).values(**user.model_dump()).returning(UserProfile)
    user = list((await execute_command(query, commit_after_execute=True)).scalars())[0]
    return UserGet(**user.to_dict())


@router.get("", dependencies=[Depends(get_current_user)])
async def get_users() -> list[UserGet]:
    users = await UserProfile.get_all()
    return [UserGet(**user.to_dict()) for user in users]


@router.post("/avatar")
async def post_new_avatar(
    file: UploadFile, current_user=Depends(get_current_user)
) -> UserGet:
    if file.size >= MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Avatar size {file.size} is too big!",
        )

    content_type = file.headers.get("content-type", "")
    if not content_type.startswith("image"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Avatar could be only as image not {content_type}",
        )

    image_id = str(uuid4())
    with (AVATARS_DIR / image_id).open("wb") as f:
        f.write(await file.read())

    # fmt: off
    query = (
        update(UserProfile)
        .where(UserProfile.id == current_user.id)
        .values(avatar=f"/avatars/{image_id}")
        .returning(UserProfile)
    )
    # fmt: on
    user = list((await execute_command(query, commit_after_execute=True)).scalars())[0]
    return UserGet(**user.to_dict())


@router.get("/by_username/{username}", dependencies=[Depends(get_current_user)])
async def get_id_by_username(username: str) -> UserGet:
    user = await UserProfile.get(username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with this username is not found",
        )
    return UserGet(**user.to_dict())
