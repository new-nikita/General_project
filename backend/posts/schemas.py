from backend.core.schemas.base_content_schemas import (
    ContentCreate,
    ContentUpdate,
    ContentRead,
)


class PostCreate(ContentCreate): ...


class PostUpdate(ContentUpdate): ...


class PostRead(ContentRead): ...
