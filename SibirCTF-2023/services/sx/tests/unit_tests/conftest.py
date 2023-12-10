import pytest
from sqlalchemy import insert
from sqlalchemy.sql.ddl import CreateTable, DropTable

from app.db import get_async_session, BaseModel, execute_command
from app.models import UserProfile, Subscribe, Post
from app.utils.auth import create_user_token


@pytest.fixture
def base_url() -> str:
    return "http://test"


@pytest.fixture(autouse=True)
async def test_db() -> None:
    async_session = get_async_session()

    async with async_session() as session:
        for table in BaseModel.metadata.sorted_tables:
            drop_expression = DropTable(table, if_exists=True)
            await session.execute(drop_expression)

            create_expression = CreateTable(table, if_not_exists=True)
            await session.execute(create_expression)


async def create_user(username: str) -> UserProfile:
    attrs = {
        "username": username,
        "fullname": "",
        "bio": "",
        "password": "test-pass",
    }
    query = insert(UserProfile).values(**attrs).returning(UserProfile)
    user = list((await execute_command(query, commit_after_execute=True)).scalars())[0]
    return user


@pytest.fixture
async def user() -> UserProfile:
    return await create_user("test-user")


@pytest.fixture
async def user2() -> UserProfile:
    return await create_user("test-user-2")


@pytest.fixture
async def user3() -> UserProfile:
    return await create_user("test-user-3")


async def create_post(
    author: str,
    title: str,
    content: str = "",
    repost_on: str | None = None,
    is_private: bool = True,
    **kwargs,
) -> Post:
    attrs = {
        "author": author,
        "title": title,
        "content": content,
        "repost_on": repost_on,
        "is_private": is_private,
    } | kwargs
    query = insert(Post).values(**attrs).returning(Post)
    post = list((await execute_command(query, commit_after_execute=True)).scalars())[0]
    return post


@pytest.fixture
async def user_post1(user: UserProfile) -> Post:
    return await create_post(author=user.id, title="Test post1 by user")


@pytest.fixture
async def user_post2(user: UserProfile) -> Post:
    return await create_post(
        author=user.id, title="Test post2 by user", is_private=False
    )


@pytest.fixture
async def subscribe(user: UserProfile, user2: UserProfile) -> Subscribe:
    attrs = {"subscriber": user.id, "subscribe_profile": user2.id}
    query = insert(Subscribe).values(**attrs).returning(Subscribe)
    return list((await execute_command(query, commit_after_execute=True)).scalars())[0]


@pytest.fixture
async def headers(user: UserProfile) -> dict[str, str]:
    token_attrs = await create_user_token(user.id)
    token = token_attrs["access_token"]
    return {"Authorization": f"bearer {token}"}


@pytest.fixture
async def user2_headers(user2: UserProfile) -> dict[str, str]:
    token_attrs = await create_user_token(user2.id)
    token = token_attrs["access_token"]
    return {"Authorization": f"bearer {token}"}
