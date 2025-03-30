from fastapi import FastAPI
import uvicorn

from auth import routers, registration_user


app = FastAPI()

app.include_router(routers.router)
app.include_router(registration_user.router)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)  # автоматическое обновление при сохранение