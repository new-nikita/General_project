from fastapi import APIRouter, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig
from pydantic import BaseModel


router = APIRouter(tags=["Users"])

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_key"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)


class User(BaseModel):
    username: str
    password: str


@router.post('/login')
def login(creds: User, response: Response):
    if creds.username == 'test' and creds.password == 'test':
        # создается токен id пользователя
        token = security.create_access_token(uid='12345')
        # передача куки
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}

    # ошибка которую получит пользователь, ВАЖНО указать код ошибки 401
    raise HTTPException(status_code=401, detail='Incorrect username or password')


# Проверяем, зарегистрированный пользователь или нет
@router.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    # пример данных на отправления если пользователь зарегистрирован
    return {"data": "TOP SECRET"}

