import logging
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from backend.auth.authorization import get_current_user_from_cookie
from backend.core.models import User
from backend.posts.services import PostService
from backend.posts.dependencies import get_post_service
from backend.posts.schemas import PostCreate, PostUpdate, PostRead
from backend.utils.save_images import upload_image

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
    await post_service.repository.delete(post=post)
    return {"message": "Пост успешно удален"}


@router.patch("/posts/update/{post_id}", status_code=200)
async def update_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    content: str = Form(...),
    image: UploadFile | None = File(None),
) -> JSONResponse:
    """
    Обработчик обновления поста.

    Принимает текстовое содержимое и/или новое изображение.
    Обновляет пост в базе данных и возвращает обновлённые данные.

    :param post_id: ID поста для обновления.
    :param current_user: Авторизованный пользователь (получается из куки).
    :param post_service: Сервис для работы с постами.
    :param content: Новое текстовое содержимое поста (обязательное).
    :param image: Новое изображение (опционально).

    :return: JSON-ответ с данными обновлённого поста.
    :raises HTTPException: Если пост не найден или у пользователя нет прав на редактирование.
    """

    post = await post_service.repository.get_by_id(id_=post_id)
    if not post:
        logger.error(f"Пост с ID {post_id} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден"
        )

    # Проверяем права пользователя
    if post.author_id != current_user.id and not current_user.is_superuser:
        logger.error(
            f"Пользователь с ID {current_user.id} не имеет прав на изменение поста с ID {post_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на редактирование этого поста",
        )
    image_url = post.image
    if image and image.filename:
        try:
            image_url = await upload_image(
                user_id=current_user.id, image_file=image, content_path="posts/images"
            )
        except Exception as e:
            logger.error(f"Не удалось загрузить изображение: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при обработке изображения",
            )

    post_dto = PostUpdate(content=content, image=image_url, author_id=current_user.id)

    try:
        updated_post = await post_service.repository.update(
            post=post, update_data=post_dto
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении поста: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить пост",
        )

    return JSONResponse(
        content={"post": PostRead.model_validate(updated_post).model_dump()}
    )


@router.post("/posts/remove-image/{post_id}")
async def remove_post_image(
    post_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    post_service: PostService = Depends(get_post_service),
):
    post = await post_service.repository.get_by_id(post_id)

    if not post or post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=404, detail="Пост не найден или недостаточно прав"
        )

    result = await post_service.repository.remove_image(post)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result["message"])

    return result
