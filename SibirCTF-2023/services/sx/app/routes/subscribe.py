from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from app.db import execute_command
from app.models import Subscribe, UserProfile
from app.schemas import UserGet
from app.utils.auth import get_current_user


router = APIRouter(prefix="/subscribes", tags=["Subscribe"])


@router.get("/following")
async def get_users_who_you_re_subscribed(
    current_user=Depends(get_current_user),
) -> list[UserGet]:
    # fmt: off
    query = (
        select(UserProfile)
        .join(Subscribe, UserProfile.id == Subscribe.subscribe_profile)
        .where(Subscribe.subscriber == current_user.id)
        .order_by(UserProfile.created_at.desc())
    )
    users = list((await execute_command(query)).scalars())
    # fmt: on
    return [UserGet(**user.to_dict()) for user in users]


@router.get("/followers")
async def get_users_who_subscribe_you(
    current_user=Depends(get_current_user),
) -> list[UserGet]:
    # fmt: off
    query = (
        select(UserProfile)
        .join(Subscribe, UserProfile.id == Subscribe.subscriber)
        .where(Subscribe.subscribe_profile == current_user.id)
        .order_by(UserProfile.created_at.desc())
    )
    users = list((await execute_command(query)).scalars())
    # fmt: on
    return [UserGet(**user.to_dict()) for user in users]


@router.put("/{profile_id}")
async def subscribe_on_profile(
    profile_id: str, current_user=Depends(get_current_user)
) -> JSONResponse:
    if str(profile_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't subscribe on yourselfe",
        )

    if await Subscribe.get(subscriber=current_user.id, subscribe_profile=profile_id):
        return JSONResponse(
            content="You already subscribed!", status_code=status.HTTP_200_OK
        )

    query = insert(Subscribe).values(
        subscriber=current_user.id, subscribe_profile=profile_id
    )
    await execute_command(query, commit_after_execute=True)
    return JSONResponse(content="Created!", status_code=status.HTTP_201_CREATED)
