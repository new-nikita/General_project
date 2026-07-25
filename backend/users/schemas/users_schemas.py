from datetime import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic.functional_validators import AfterValidator

from backend.utils.validated import validate_username
from backend.users.schemas.profile_schemas import ProfileCreate, ProfileResponse


class UserBase(BaseModel):
    username: Annotated[
        str, MinLen(3), MaxLen(20), AfterValidator(validate_username)
    ] = Field(
        description="Username must be between 3 and 20 characters, only letters, numbers, underscores"
    )
    email: Annotated[EmailStr, MaxLen(100)] = Field(
        description="Valid email address, max 100 chars"
    )


class UserCreate(UserBase):
    password: Annotated[str, MinLen(8)] = Field(
        description="Password must contain at least 8 characters"
    )
    profile: ProfileCreate | None = None


class UserUpdate(UserBase):
    username: Annotated[
        str | None,
        MinLen(3),
        MaxLen(20),
        AfterValidator(validate_username),
    ] = Field(
        default=None,
        description="Username must be between 3 and 20 characters, only letters, numbers, underscores",
    )
    email: Annotated[EmailStr | None, MaxLen(100)] = Field(
        default=None, description="Valid email address, max 100 chars"
    )
    password: Annotated[str | None, MinLen(8)] = Field(
        default=None, description="Password must contain at least 8 characters"
    )
    profile: ProfileCreate | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
