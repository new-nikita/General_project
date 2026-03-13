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

router = APIRouter()


@router.get("/posts/{post_id}/comments_form", tags=["comments"])
async def get_comments_html(
    request: Request,
    post_id: int,
):

    return settings.templates.template_dir.TemplateResponse(
        "comments/comment_form.html",
        {
            "request": request,
            "post_id": post_id,
        },
    )


@router.post(
    "/posts/{post_id}/comments",
    tags=["comments"],
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    service: Annotated[CommentService, Depends(get_comment_service)],
    content: str = Form(...),
):
    return await service.create_comment(
        user_id=current_user.id,
        post_id=post_id,
        text=content,
        parent_id=None,
    )


@router.get("/posts/{post_id}/comments", tags=["comments"])
async def get_paginated_comments(
    request: Request,
    post_id: int,
    service: Annotated[CommentService, Depends(get_comment_service)],
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    offset: int = 0,
    limit: int = 5,
):
    comments, has_more = await service.get_paginated_comments(post_id, offset, limit)

    return settings.templates.template_dir.TemplateResponse(
        "comments/comments_list.html",
        {
            "request": request,
            "comments": comments,
            "has_more": has_more,
            "offset": offset + limit,
            "limit": limit,
            "current_user": current_user,
            "post_id": post_id,
        },
    )
