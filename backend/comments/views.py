from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from backend.core.models import User, Post
from backend.auth.authorization import get_current_user_from_cookie
from backend.posts.dependencies import get_post_service
from backend.posts.services import PostService

router = APIRouter()


@router.post("/posts/{post_id}/comment")
async def create_comment(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
) -> JSONResponse:
    pass
