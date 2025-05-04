from fastapi.templating import Jinja2Templates
from pathlib import Path


class TemplateManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.templates = Jinja2Templates(directory=str(base_dir))

    def __getattr__(self, name: str):
        # Возвращает новый экземпляр TemplateManager для подкаталога
        sub_dir = self.base_dir / name
        return TemplateManager(sub_dir)

    def TemplateResponse(self, template_name: str, context: dict):
        return self.templates.TemplateResponse(template_name, context)


# TOODO - возмжно сделать доступ до директории через __getattr__
# по такому типу
"""
@router.get("/{profile_id}", response_class=HTMLResponse)
async def get_user_profile(
    request: Request,
    profile_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    is_own_profile: bool = False,
) -> HTMLResponse:
    profile_user = await user_service.repository.get_by_id(profile_id)
    if not profile_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {profile_id} не найден",
        )
    if current_user is not None:
        is_own_profile = current_user.id == profile_user.id

    posts = await post_service.repository.get_all_posts_by_author_id(profile_id)
    return settings.templates.template_manager.users.TemplateResponse(     <<===используем шаблонизатор
        "profile.html", <<=== передаём без 'users/' так, как она будет искать в папке users ведь её указали в template_manager.users
        {
            "request": request,
            "user": profile_user,
            "is_own_profile": is_own_profile,
            "current_user": current_user,
            "posts": posts,
        },
    )
"""
