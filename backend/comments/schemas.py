from typing import Optional

from pydantic import BaseModel

from backend.core.schemas.base_content_schemas import (
    ContentCreate,
    ContentUpdate,
    ContentRead,
)


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(ContentUpdate):
    text: Optional[str] = None


class CommentRead(ContentRead):
    post_id: int
    text: str
    user_id: int
    parent_id: Optional[int] = None
    replies: Optional[list["CommentRead"]] = None

    class Config:
        from_attributes = True
