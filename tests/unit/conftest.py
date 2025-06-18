import pytest
from tests.factories.profile_factory import (
    create_profile_create_data,
    create_profile_create_none_fields,
)


@pytest.fixture
def profile_create_data():
    return create_profile_create_data()


@pytest.fixture
def profile_create_none_fields():
    return create_profile_create_none_fields()
