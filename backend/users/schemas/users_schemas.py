from datetime import datetime

from typing import Annotated
from annotated_types import MinLen, MaxLen

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    constr,
)
from pydantic.functional_validators import AfterValidator

from utils.validated import validate_username
from users.schemas.profile_schemas import ProfileCreate


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=20) = Field(
        ...,
        description="Username must be between 3 and 20 characters "
        "and can only contain letters, numbers, and underscores",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password must contain at least 8 characters",
    )
    email: EmailStr = Field(..., max_length=100)
    profile: ProfileCreate | None = None


class UserUpdate(BaseModel):
    username: Annotated[
        str | None, MinLen(3), MaxLen(20), AfterValidator(validate_username)
    ] = None
    password: Annotated[
        str | None,
        MinLen(8),
        Field(description="Password must contain at least 8 characters"),
    ] = None
    email: Annotated[EmailStr | None, Field(..., max_length=100)] = None


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
