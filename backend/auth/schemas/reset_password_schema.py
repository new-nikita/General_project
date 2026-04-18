from pydantic import BaseModel, EmailStr


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str


class MessageResponse(BaseModel):
    message: str
    success: bool = True
