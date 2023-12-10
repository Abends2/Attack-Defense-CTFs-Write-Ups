import pytest
from httpx import AsyncClient

from app.main import app as app_
from app.models import UserProfile


@pytest.mark.asyncio
async def test_user_post(base_url: str):
    body = {
        "username": "test_user",
        "fullname": "Test User",
        "bio": "",
        "password": "test_pass",
    }
    async with AsyncClient(app=app_, base_url=base_url) as client:
        response = await client.post("/users", json=body)
    assert response.status_code == 200
    response_data = response.json()

    user = await UserProfile.get(id=response_data["id"])
    assert user.username == body["username"]


@pytest.mark.asyncio
async def test_user_get(base_url: str, headers: dict, user: UserProfile):
    async with AsyncClient(app=app_, base_url=base_url, headers=headers) as client:
        response = await client.get("/users")
    assert response.status_code == 200

    assert response.json() == [
        {
            "bio": "",
            "fullname": "",
            "id": str(user.id),
            "username": "test-user",
            "avatar": None,
        },
    ]
