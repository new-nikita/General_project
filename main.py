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


main_app = create_app()

main_app.include_router(profile_router)
main_app.include_router(auth_router)
main_app.include_router(posts_router)
main_app.include_router(likes_router)
main_app.include_router(comments_router)
main_app.include_router(friends_router)
main_app.include_router(followers_router)
main_app.include_router(messages_router)

main_app.add_middleware(TokenRefreshMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
