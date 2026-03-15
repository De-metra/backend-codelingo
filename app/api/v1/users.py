from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form

from app.schemas.user import UserReturn
from app.core.security import  get_user_from_token
from app.services.user_service import UserService
from app.utils.dependencies import get_user_service
from app.core.exception import (
    AppError, StatsNotFoundError,
    UserNotFoundError, NoneDataToUpdate,
    CourseNotFoundError
)


router = APIRouter()

@router.get("/stats/")
async def get_users_stats(
    current_user: str = Depends(get_user_from_token), 
    user_service: UserService = Depends(get_user_service)
):
    """Получаем статистику конкретного пользователя."""
    try:
        return await user_service.get_user_stats(int(current_user))
    except StatsNotFoundError: 
        raise HTTPException(status_code=404, detail="Статистика не найдена")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get("/me/", response_model=UserReturn)
async def get_me(
    current_user: str = Depends(get_user_from_token), 
    user_service: UserService = Depends(get_user_service)
):
    """
    Этот маршрут защищен и требует токен. Если токен действителен, мы возвращаем информацию о пользователе.
    """
    try:
        return await user_service.get_user_with_stats(user_id=int(current_user))
    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.patch("/change-me/")  #patch   
async def change_profile(
    username: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    current_user: str = Depends(get_user_from_token), 
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.change_me(
            user_id=int(current_user),
            username=username,
            file=file
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не найден"
        )
    except NoneDataToUpdate:
        return {}
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post("/change-avatar/")
async def change_avatar(
    file: UploadFile = File(...),
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.change_avatar(int(current_user), file)
    except UserNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не найден"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post("/delete-me/")
async def soft_delete(
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.soft_delete_account(int(current_user)) 
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get("/course")
async def get_users_course(
    current_user: str = Depends(get_user_from_token), 
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.get_user_course(int(current_user))
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
