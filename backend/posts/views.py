import logging
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from auth.authorization import get_current_user_from_cookie
from core.models import User
from posts.services import PostService
from posts.dependencies import get_post_service
from posts.schemas import PostCreate
from utils.save_images import upload_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/posts/create")
async def create_new_post(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    content: str = Form(..., description="Текстовое содержимое поста"),
    image: UploadFile = File(None, description="Изображение для поста (опционально)"),
) -> JSONResponse:
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
    if image and image.filename:
        image_url = await upload_image(
            user_id=current_user.id, image_file=image, content_path="posts/images"
        )
    else:
        image_url = None

    post_dto = PostCreate(
        content=content,
        image=image_url,
        author_id=current_user.id,
    )

    new_post = await post_service.create_post_and_add_in_db(post_dto)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "post": {
                "id": new_post.id,
                "content": new_post.content,
                "image": new_post.image,
                "author": {
                    "profile": {
                        "avatar": current_user.profile.avatar,
                        "full_name": current_user.profile.full_name,
                    }
                },
                "created_at": new_post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        },
    )


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
