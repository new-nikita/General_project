from typing import Optional, Self

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, Field, field_validator, model_validator


class ContentBase(BaseModel):
    """
    Базовая схема для поста — содержит общие поля и валидации
    """

    content: str | None = Field(..., description="Содержимое поста")
    image: Optional[str] = Field(default=None, description="Изображение поста")

    model_config = {"from_attributes": True}

    @field_validator("content")
    def validate_content(cls, value: str | None) -> str | None:
        # Проверяем, что содержимое не состоит только из пробелов

        if not value or not value.strip():
            return
        return value


class ContentCreate(ContentBase):
    """
    Схема для создания поста
    """

    author_id: int = Field(..., description="ID автора поста")

    @field_validator("image")
    def validate_image(cls, image: str | None) -> Optional[str]:
        if not image:
            return

        allowed_extensions = (".jpg", ".jpeg", ".png", ".gif", ".JPG")
        if not image.endswith(allowed_extensions):
            raise ValueError("Некорректное расширение файла изображения")
        return image

    @model_validator(mode="after")
    def validate_post_has_content_or_image(self) -> Self:
        # Проверяем, что пост не пустой (есть текст или изображение)
        if not self.content and self.image is None:
            raise ValueError("Пост должен содержать текст или изображение")
        return self


class ContentUpdate(ContentCreate):
    """
    Схема для обновления поста
    """

    content: Optional[str] = None
    image: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        content: str = Form(...),
        image: UploadFile | str | None = File(None),
        author_id: int = Form(...),
    ):
        return cls(content=content, image=image, author_id=author_id)


class ContentRead(ContentBase):
    """
    Схема для отображения информации о посте
    """

    id: int = Field(..., description="ID поста")
    author_id: int = Field(..., description="ID автора поста")
