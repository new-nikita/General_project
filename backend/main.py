import logging

import uvicorn
from core.config import settings

from create_app import create_app

from auth.router import router as auth_router
from users.views import router as profile_router
from core.middleware import TokenRefreshMiddleware

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)

main_app = create_app()

main_app.include_router(profile_router)
main_app.include_router(auth_router)

main_app.add_middleware(TokenRefreshMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        reload=True,
    )
