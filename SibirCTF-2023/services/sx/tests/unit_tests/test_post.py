from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.main import app as app_
from app.models import Post, UserProfile, Subscribe


@pytest.mark.asyncio
async def test_create_post(base_url: str, headers: dict):
    body = {
        "title": "My test post",
        "content": "...",
        "is_private": True,
        "repost_on": None,
    }
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.post("/posts", json=body)
    assert response.status_code == 200
    response_data = response.json()

    post = await Post.get(id=response_data["id"])
    assert post.title == body["title"]
    assert post.content == body["content"]
    assert post.is_private == body["is_private"]
    assert post.repost_on == body["repost_on"]


@pytest.mark.asyncio
async def test_create_post__nonexistent_repost_on(base_url: str, headers: dict):
    body = {
        "title": "My test post",
        "content": "...",
        "is_private": True,
        "repost_on": str(uuid4()),
    }
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.post("/posts", json=body)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Such repost not found (parameter 'repost_on')"
    }


@pytest.mark.asyncio
async def test_create_post__existent_repost_on(
    base_url: str, headers: dict, user_post1: Post
):
    body = {
        "title": "My test post",
        "content": "...",
        "is_private": True,
        "repost_on": user_post1.id,
    }
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.post("/posts", json=body)
    assert response.status_code == 200
    response_data = response.json()

    post = await Post.get(id=response_data["id"])
    assert post.repost_on == user_post1.id


@pytest.mark.asyncio
async def test_update_post(base_url: str, headers: dict, user_post1: Post):
    assert user_post1.is_private
    assert user_post1.updated_at is None
    body = {"is_private": False}
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.patch(f"/posts/{user_post1.id}", json=body)
    assert response.status_code == 200, response.json()
    response_data = response.json()

    assert response_data["id"] == user_post1.id
    post = await Post.get(id=response_data["id"])
    assert not post.is_private
    assert post.updated_at


@pytest.mark.asyncio
async def test_get_your_post(
    base_url: str, headers: dict, user: UserProfile, user_post1: Post
):
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.get(f"/posts/{user_post1.id}")
    assert response.status_code == 200, response.json()
    assert response.json() == {
        "author": user.id,
        "content": "",
        "created_at": user_post1.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        "id": user_post1.id,
        "is_private": True,
        "repost_on": None,
        "title": "Test post1 by user",
        "updated_at": None,
    }


@pytest.mark.asyncio
async def test_get_not_yours_private_post__nok(
    base_url: str, user2_headers: dict, user_post1: Post
):
    async with AsyncClient(
        app=app_, base_url=base_url, headers=user2_headers
    ) as client:
        response = await client.get(f"/posts/{user_post1.id}")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You don't have permissions to read a private post"
    }


@pytest.mark.asyncio
async def test_get_not_yours_private_post__ok(
    base_url: str, user2_headers: dict, user_post1: Post, subscribe: Subscribe
):
    async with AsyncClient(
        app=app_, base_url=base_url, headers=user2_headers
    ) as client:
        response = await client.get(f"/posts/{user_post1.id}")
    assert response.status_code == 200
    assert response.json()["content"] == user_post1.content


@pytest.mark.asyncio
async def test_get_posts_from_another_account__without_subscribe(
    base_url: str,
    user: UserProfile,
    user2_headers: dict,
    user_post1: Post,
    user_post2: Post,
):
    async with AsyncClient(
        app=app_, base_url=base_url, headers=user2_headers
    ) as client:
        response = await client.get(f"/posts/user/{user.id}")
    assert response.status_code == 200, response.json()
    assert response.json() == [
        {
            "author": user.id,
            "content": "",
            "created_at": user_post2.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "id": user_post2.id,
            "is_private": False,
            "repost_on": None,
            "title": "Test post2 by user",
            "updated_at": None,
        }
    ]


@pytest.mark.asyncio
async def test_get_posts_from_another_account__with_subscribe(
    base_url: str,
    user: UserProfile,
    user2_headers: dict,
    user_post1: Post,
    user_post2: Post,
    subscribe: Subscribe,
):
    async with AsyncClient(
        app=app_, base_url=base_url, headers=user2_headers
    ) as client:
        response = await client.get(f"/posts/user/{user.id}")
    assert response.status_code == 200, response.json()
    posts_titles = [post["title"] for post in response.json()]
    assert set(posts_titles) == {"Test post1 by user", "Test post2 by user"}
