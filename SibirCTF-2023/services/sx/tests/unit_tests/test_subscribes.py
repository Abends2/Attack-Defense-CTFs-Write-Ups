import pytest
from httpx import AsyncClient

from app.main import app as app_
from app.models import UserProfile, Subscribe
from app.utils.auth import create_user_token


@pytest.mark.asyncio
async def test_get_subscribes(
    base_url: str, headers: dict, user2: UserProfile, subscribe: Subscribe
):
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.get("/subscribes/following")
    assert response.status_code == 200

    assert response.json() == [
        {
            "bio": "",
            "fullname": "",
            "id": user2.id,
            "username": "test-user-2",
            "avatar": None,
        }
    ]


@pytest.mark.asyncio
async def test_get_users_who_subscribes_you(
    base_url: str,
    user: UserProfile,
    user2: UserProfile,
    subscribe: Subscribe,
    user2_headers: dict,
):
    async with AsyncClient(
        app=app_, base_url=base_url, headers=user2_headers
    ) as client:
        response = await client.get("/subscribes/followers")
    assert response.status_code == 200

    assert response.json() == [
        {
            "bio": "",
            "fullname": "",
            "id": user.id,
            "username": "test-user",
            "avatar": None,
        }
    ]


@pytest.mark.asyncio
async def test_put_new_subscribe(
    base_url: str, user: UserProfile, user2: UserProfile, headers: dict
):
    subscribe = await Subscribe.get(subscriber=user.id)
    assert not subscribe

    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.put(f"/subscribes/{user2.id}")
    assert response.status_code == 201

    subscribe = await Subscribe.get(subscriber=user.id)
    assert subscribe.subscriber == user.id
    assert subscribe.subscribe_profile == user2.id


@pytest.mark.asyncio
async def test_put_existent_subscribe(
    base_url: str,
    user: UserProfile,
    user2: UserProfile,
    headers: dict,
    subscribe: Subscribe,
):
    subscribes = await Subscribe.get_all(subscriber=user.id)
    assert len(subscribes) == 1

    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.put(f"/subscribes/{user2.id}")
    assert response.status_code == 200

    subscribes = await Subscribe.get_all(subscriber=user.id)
    assert len(subscribes) == 1
