from pydantic import BaseModel, EmailStr


class InitialRegisterRequest(BaseModel):
    email: EmailStr
    client: str | None = None


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    password2: str

    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    phone_number: str | None = None
    country: str | None = None
    city: str | None = None
    street: str | None = None
    bio: str | None = None


class MessageResponse(BaseModel):
    message: str
    email: str | None = None
    user_id: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str
