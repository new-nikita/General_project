from typing import Optional
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    constr,
    field_validator,
    ValidationError,
)


class PostBase(BaseModel):
    """
    Базовая схема для поста
    """

    content: constr(min_length=0) = Field(..., description="Содержимое поста")
    is_published: bool = Field(default=True, description="Опубликован ли пост")
    image: Optional[str] = Field(default=None, description="Изображение поста")

    model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
    """
    Схема для создания поста
    """

    author_id: int = Field(..., description="ID автора поста")

    @field_validator("image")
    def validate_image(cls, image: str) -> Optional[str]:
        if not image:
            return

        if not image.endswith((".jpg", ".png", ".jpeg", ".gif")):
            raise ValueError("Некорректное расширение файла изображения")
        return image


class PostRead(PostBase):
    """
    Схема для отображения информации о посте
    """

    id: int = Field(..., description="ID поста")
    author_id: int = Field(..., description="ID автора поста")
