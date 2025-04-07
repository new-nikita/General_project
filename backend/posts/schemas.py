from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, constr


class TagBase(BaseModel):
    """
    Определяет минимальную схему для тегов.
    """
    id: Optional[int] = Field(None, description="ID тега")
    name: constr(min_length=1, max_length=50) = Field(..., description="Название тега")

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    """
    Базовая схема для поста
    """
    title: constr(min_length=1, max_length=100) = Field(..., description="Заголовок поста")
    content: constr(min_length=1) = Field(..., description="Содержимое поста")
    is_published: bool = Field(default=False, description="Опубликован ли пост")

    model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
    """
    Схема для создания поста
    """
    author_id: int = Field(..., description="ID автора поста")
    # При создании поста можно передавать список названий тегов,
    # которые потом будут сопоставлены с моделью Tag
    tags: List[str] = Field(default=[], description="Список названий тегов")


class PostRead(PostBase):
    """
    Схема для отображения информации о посте
    """
    id: int = Field(..., description="ID поста")
    author_id: int = Field(..., description="ID автора поста")
    # При чтении поста возвращаем список тегов в виде объектов TagBase
    tags: List[TagBase] = Field(default=[], description="Список тегов, связанных с постом")
