import logging
import os
import uuid
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status

from auth.authorization import get_current_user_from_cookie
from core.models import User
from posts.services import PostService
from posts.dependencies import get_post_service
from posts.schemas import PostCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Путь для сохранения изображений постов
POST_IMAGES_DIR = "static/posts/images"
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ


def validate_image_size(file_size: int) -> None:
    """
    Проверяет размер файла.

    :param file_size: Размер файла
    :raises HTTPException: Если размер файла превышает лимит.
    """
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла превышает допустимый лимит (5 МБ).",
        )


def generate_image_path(user_id: int, filename: str) -> str:
    """
    Генерирует уникальный путь для сохранения изображения.

    :param user_id: ID пользователя.
    :param filename: Имя загруженного файла.
    :return: Полный путь к файлу.
    """
    unique_filename = f"{uuid.uuid4()}_{filename}"
    user_dir = os.path.join(POST_IMAGES_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)  # Создаем директорию, если она не существует
    return os.path.join(user_dir, unique_filename)


async def save_image_to_disk(image_path: str, image_file: UploadFile) -> None:
    """
    Сохраняет изображение на диск.

    :param image_path: Путь для сохранения изображения.
    :param image_file: Загруженный файл.
    :raise HTTPException: Если произошла ошибка при записи файла.
    """
    try:
        with open(image_path, "wb") as buffer:
            buffer.write(await image_file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении изображения: {str(e)}",
        )


def format_image_url(image_path: str) -> str:
    """
    Форматирует путь к изображению для хранения в базе данных.

    :param image_path: Полный путь к файлу на диске.
    :return: Путь к изображению на сервере.
    """
    return f"/{image_path}" if image_path else None


@router.post("/posts/create")
async def create_new_post(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    content: str = Form(..., description="Текстовое содержимое поста"),
    image: UploadFile = File(None, description="Изображение для поста (опционально)"),
) -> dict:
    """
    Создает новый пост для авторизованного пользователя.
    :param current_user: Текущий авторизованный пользователь.
    :param post_service: Сервис для работы с постами.
    :param content: Текстовое содержимое поста.
    :param image: Загруженное изображение для поста.

    :return: Ответ с информацией о созданном посте.
    """
    if not content and image.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пост не может быть пустым."
        )
    image_url = None
    if image and image.filename:
        try:
            validate_image_size(image.size)
            image_path = generate_image_path(current_user.id, image.filename)
            await save_image_to_disk(image_path, image)
            image_url = format_image_url(image_path)
        except HTTPException as e:
            raise e  # Пробрасываем ошибку дальше

    post_dto = PostCreate(
        content=content,
        image=image_url,
        author_id=current_user.id,
    )

    new_post = await post_service.create_post_and_add_in_db(post_dto)

    return {
        "post": {
            "content": new_post.content,
            "image": new_post.image,
            "author": {
                "profile": {
                    "avatar": current_user.profile.avatar,
                    "full_name": current_user.profile.full_name,
                }
            },
            "created_at": new_post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        },
    }


@router.post("/posts/delete/{post_id}")
async def delete_post(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    post_id: int,
) -> dict[str, str]:
    """
    Удаляет пост по его ID.

    :param current_user: Текущий авторизованный пользователь.
    :param post_service: Сервис для работы с постами.
    :param post_id: ID поста.

    :return: Сообщение об успешном удалении.
    :raises HTTPException: Если пост не найден или у пользователя недостаточно прав.
    """
    # Получаем пост из базы данных
    post = await post_service.repository.get_post_by_id(post_id=post_id)
    if not post:
        logger.error(f"Пост с ID {post_id} не найден")
        raise HTTPException(status_code=404, detail="Пост не найден")

    # Проверяем права пользователя
    if post.author_id != current_user.id and not current_user.is_superuser:
        logger.error(
            f"Пользователь с ID {current_user.id} не имеет прав на удаление поста с ID {post_id}"
        )
        raise HTTPException(
            status_code=403, detail="У вас нет прав на удаление этого поста"
        )

    # Удаляем пост
    await post_service.repository.delete(id_=post_id)
    return {"message": "Пост успешно удален"}
