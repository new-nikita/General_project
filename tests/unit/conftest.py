from typing import TYPE_CHECKING
import pytest

from tests.factories.profile_factory import (
    create_profile_create_data,
    create_profile_create_none_fields,
)
from tests.factories.content_factory import ContentCreateFactory

if TYPE_CHECKING:
    from backend.core.schemas.base_content_schemas import ContentCreate
    from backend.users.schemas.profile_schemas import ProfileCreate


@pytest.fixture
def profile_create_data() -> "ProfileCreate":
    return create_profile_create_data()


@pytest.fixture
def profile_create_none_fields() -> "ProfileCreate":
    return create_profile_create_none_fields()


@pytest.fixture
def valid_content_data() -> "ContentCreate":
    """Возвращает валидный объект ContentCreate."""
    return ContentCreateFactory.build()


@pytest.fixture
def valid_content_with_only_text() -> "ContentCreate":
    return ContentCreateFactory.build_only_text()


@pytest.fixture
def valid_content_with_only_image() -> "ContentCreate":
    return ContentCreateFactory.build_only_image()
