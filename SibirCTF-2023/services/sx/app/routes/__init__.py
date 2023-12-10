from fastapi import APIRouter

from . import (
    user_profile,
    session,
    subscribe,
    post,
    feed,
)


routers = (
    user_profile.router,
    subscribe.router,
    post.router,
    feed.router,
    session.router,
)

router = APIRouter()
for router_item in routers:
    router.include_router(router_item)
