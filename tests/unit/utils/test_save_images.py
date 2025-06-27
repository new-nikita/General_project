import os
import tempfile
import shutil
import pytest
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from unittest.mock import AsyncMock, patch

from backend.utils.save_images import (
    validate_image_size,
    generate_image_path,
    format_image_url,
    save_image_to_disk,
    upload_image,
    ERROR_MESSAGE_BY_LIMIT_SIZE,
    ERROR_MESSAGE_BY_INCORRECT_SIZE,
    MAX_MB,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "size_mb",
    [
        pytest.param(1, id="1MB"),
        pytest.param(2, id="2MB"),
        pytest.param(3, id="3MB"),
        pytest.param(4, id="4MB"),
        pytest.param(5, id="5MB"),
        pytest.param(0.5, id="0.5MB"),
        pytest.param(1.5, id="1.5MB"),
        pytest.param(2.2, id="2.2MB"),
        pytest.param(3.3, id="3.3MB"),
        pytest.param(4.4, id="4.4MB"),
        pytest.param(5.0, id="5.0MB_float"),
    ],
)
async def test_validate_image_size_accepts_valid_size(size_mb: float) -> None:
    """Проверка допустимых размеров файлов."""
    size_bytes = int(size_mb * 1024 * 1024)
    with patch("backend.utils.save_images.MAX_IMAGE_SIZE", 5 * 1024 * 1024):
        try:
            assert validate_image_size(size_bytes) is True
            assert validate_image_size(size_bytes) is not None
        except HTTPException as e:
            pytest.fail(
                f"Валидация неожиданно провалилась для размера {size_mb}MB: {e}"
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "size_mb, exception_message",
    [
        (MAX_MB + 0.1, ERROR_MESSAGE_BY_LIMIT_SIZE),
        (zero := 0, ERROR_MESSAGE_BY_INCORRECT_SIZE.format(zero)),
    ],
)
async def test_validate_image_size_raises_for_large_size(
    size_mb: int,
    exception_message: str,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        validate_image_size(size_mb * 1024 * 1024)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == exception_message


def test_generate_image_path_creates_dir_and_returns_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        user_id = 42
        filename = "image.png"
        path = generate_image_path(user_id, filename, tmpdir)
        assert str(user_id) in path
        assert filename in path
        user_dir = os.path.join(tmpdir, str(user_id))
        assert os.path.isdir(user_dir)
        # Проверяем, что имя файла содержит uuid
        unique_part = os.path.basename(path).split("_")[0]
        uuid.UUID(unique_part)  # выбросит исключение, если не uuid


@pytest.mark.asyncio
async def test_save_image_to_disk_writes_file(tmp_path):
    content = b"test image content"
    image_path = tmp_path / "test.png"
    dummy_file = AsyncMock(spec=UploadFile)
    dummy_file.read = AsyncMock(side_effect=[content, b""])

    await save_image_to_disk(str(image_path), dummy_file)
    assert image_path.exists()
    assert image_path.read_bytes() == content


@pytest.mark.asyncio
async def test_save_image_to_disk_raises_http_exception(tmp_path):
    dummy_file = AsyncMock(spec=UploadFile)
    dummy_file.read = AsyncMock(side_effect=Exception("disk error"))

    with pytest.raises(HTTPException) as exc_info:
        await save_image_to_disk(str(tmp_path / "file.png"), dummy_file)
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Ошибка при сохранении изображения" in exc_info.value.detail
