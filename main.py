import uvicorn

from backend.auth.views import router as auth_router
from backend.users.views import router as profile_router
from backend.posts.views import router as posts_router
from backend.likes.like_router import router as likes_router
from backend.comments.views import router as comments_router
from backend.friends.views import router as friends_router
from backend.follower.views import router as followers_router
from backend.message.views import router as messages_router

from create_app import create_app
from backend.core.middleware import TokenRefreshMiddleware


app = create_app()

API_PREFIX = "/api/v1"

app.include_router(
    profile_router,
    prefix=f"{API_PREFIX}/users",
    tags=["users"],
)
app.include_router(
    auth_router,
    prefix=f"{API_PREFIX}/auth",
    tags=["auth"],
)
app.include_router(
    posts_router,
    prefix=f"{API_PREFIX}/posts",
    tags=["posts"],
)
app.include_router(
    likes_router,
    prefix=f"{API_PREFIX}/likes",
    tags=["likes"],
)
app.include_router(
    comments_router,
    prefix=f"{API_PREFIX}/comments",
    tags=["comments"],
)
app.include_router(
    friends_router,
    prefix=f"{API_PREFIX}/friends",
    tags=["friends"],
)
app.include_router(
    followers_router,
    prefix=f"{API_PREFIX}/followers",
    tags=["followers"],
)
app.include_router(
    messages_router,
    prefix=f"{API_PREFIX}/messages",
    tags=["messages"],
)

app.add_middleware(TokenRefreshMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
