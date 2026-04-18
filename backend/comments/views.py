from typing import Annotated

from fastapi import APIRouter, status, Depends, Form
from fastapi.requests import Request

from backend.comments.dependencies import get_comment_service
from backend.comments.schemas import CommentRead, CommentCreate
from backend.comments.services import CommentService
from backend.core.config import settings
from backend.core.models import User, Post
from backend.auth.authorization import get_current_user_from_cookie
from backend.posts.dependencies import get_post_service
from backend.posts.services import PostService

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/posts/{post_id}/comments",
    tags=["comments"],
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    data: CommentCreate,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    service: Annotated[CommentService, Depends(get_comment_service)],
):

    comment = service.create_comment(
        user_id=current_user.id,
        post_id=post_id,
        text=data.text,
        parent_id=data.parent_id,
    )

    return CommentRead.model_validate(comment)


@router.get("/posts/{post_id}/comments", tags=["comments"])
async def get_paginated_comments(
    request: Request,
    post_id: int,
    service: Annotated[CommentService, Depends(get_comment_service)],
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    offset: int = 0,
    limit: int = 5,
):
    comments, has_more = await service.get_paginated_comments(
        post_id,
        offset,
        limit,
    )

    return {
        "items": [CommentRead.model_validate(c) for c in comments],
        "has_more": has_more,
        "offset": offset,
        "limit": limit,
    }
