import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ
BASE_STATIC_DIR = "client_files"


async def upload_image(
    user_id: int,
    image_file: UploadFile,
    content_path: str,
) -> str:
    """
    Загружает изображение на диск и возвращает URL для доступа к нему.

    :param user_id: ID пользователя.
    :param image_file: Загруженный файл изображения.
    :param content_path: Тип контента (например, 'posts' или 'avatars').
    :return: URL для доступа к изображению.
    :raises HTTPException: Если произошла ошибка при загрузке.
    """
    # 1. Проверяем размер файла
    validate_image_size(image_file.size)

    # 2. Генерируем путь к файлу
    directory = Path(BASE_STATIC_DIR) / content_path
    image_path = generate_image_path(user_id, image_file.filename, str(directory))

    # 3. Сохраняем изображение на диск
    await save_image_to_disk(image_path, image_file)

    # 4. Форматируем URL для хранения в базе данных
    return format_image_url(image_path)


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


def generate_image_path(user_id: int, filename: str, directory: str) -> str:
    """
    Генерирует уникальный путь для сохранения изображения.

    :param user_id: ID пользователя.
    :param filename: Имя загруженного файла.
    :param directory: Директория хранения контента.
    :return: Полный путь к файлу.
    """
    unique_filename = f"{uuid.uuid4()}_{filename}"
    user_dir = os.path.join(directory, str(user_id))
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
