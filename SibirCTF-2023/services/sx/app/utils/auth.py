import asyncio
import uuid
from datetime import datetime, timedelta

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import insert

from app.db import execute_command
from app.models.user_profile import Token, UserProfile


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/session")


async def check_password(actual_passw: str, expected_passw: str, ms: int = 30) -> bool:
    if len(actual_passw) != len(expected_passw):
        return False
    for actual_symbol, expected_symbol in zip(actual_passw, expected_passw):
        if actual_symbol != expected_symbol:
            return False
        await asyncio.sleep(ms * 1e-3)
    return True


async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_obj = await Token.get(access_token=token)

    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await UserProfile.get(id=token_obj.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def create_user_token(user_id: str) -> dict:
    token = uuid.uuid4()
    expires = datetime.now() + timedelta(weeks=2)
    attrs = dict(access_token=str(token), expires=expires, user_id=user_id)
    query = insert(Token).values(**attrs)
    await execute_command(query, commit_after_execute=True)
    return attrs
