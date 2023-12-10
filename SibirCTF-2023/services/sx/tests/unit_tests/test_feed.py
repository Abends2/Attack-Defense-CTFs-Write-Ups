from datetime import datetime

import pytest
from httpx import AsyncClient

from app.main import app as app_
from app.models import UserProfile, Subscribe
from tests.unit_tests.conftest import create_post


@pytest.mark.asyncio
async def test_get_feed__following_authors_posts__feed(
    base_url: str,
    headers: dict,
    user2: UserProfile,
    user3: UserProfile,
    subscribe: Subscribe,
):
    # this post we will see
    user2_post1 = await create_post(
        author=user2.id, title="1", is_private=False, created_at=datetime.now()
    )
    # this post we won't see, because it is private
    await create_post(author=user2.id, title="2", is_private=True)
    # this post we will see
    user2_post3 = await create_post(
        author=user2.id, title="3", is_private=False, created_at=datetime.now()
    )
    # this posts we won't see, because user is not subscribed on user3
    await create_post(author=user3.id, title="4", is_private=False)
    await create_post(author=user3.id, title="5", is_private=True)

    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.get("/feed/others")
    assert response.status_code == 200, response.json()

    assert response.json() == [
        {
            "author": user2.id,
            "content": "",
            "created_at": user2_post3.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "id": user2_post3.id,
            "is_private": False,
            "repost_on": None,
            "title": "3",
            "updated_at": None,
        },
        {
            "author": user2.id,
            "content": "",
            "created_at": user2_post1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "id": user2_post1.id,
            "is_private": False,
            "repost_on": None,
            "title": "1",
            "updated_at": None,
        },
    ]


@pytest.mark.asyncio
async def test_get_feed__following_authors_posts__my(
    base_url: str,
    headers: dict,
    user: UserProfile,
    user2: UserProfile,
    subscribe: Subscribe,
):
    post_1 = await create_post(
        author=user.id, title="1", is_private=False, created_at=datetime.now()
    )
    post_2 = await create_post(
        author=user.id, title="2", is_private=True, created_at=datetime.now()
    )
    # another post
    await create_post(author=user2.id, title="3", is_private=False)

    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.get("/feed/my")
    assert response.status_code == 200, response.json()

    assert response.json() == [
        {
            "author": user.id,
            "content": "",
            "created_at": post_2.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "id": post_2.id,
            "is_private": True,
            "repost_on": None,
            "title": "2",
            "updated_at": None,
        },
        {
            "author": user.id,
            "content": "",
            "created_at": post_1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "id": post_1.id,
            "is_private": False,
            "repost_on": None,
            "title": "1",
            "updated_at": None,
        },
    ]
