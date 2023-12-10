from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import TokenBase
from app.models import UserProfile
from app.utils.auth import create_user_token, check_password


router = APIRouter(tags=["Session"], include_in_schema=False)


@router.post("/session", response_model=TokenBase)
async def auth(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = await UserProfile.get(username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    if not await check_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    return await create_user_token(user_id=user.id)
