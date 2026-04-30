from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form

from app.schemas.course import UserCourseProgressReturn, UserCourseResponse
from app.schemas.schemas import ErrorResponse, MessageReturn
from app.schemas.user import UserReturn, Stats, UserUpdatedInfo, UserChangeAvatar
from app.core.security import  get_user_from_token
from app.services.user_service import UserService
from app.utils.dependencies import get_user_service
from app.core.exception import (
    AppError, StatsNotFoundError,
    UserNotFoundError, NoneDataToUpdate,
    CourseNotFoundError, NotFoundError
)


router = APIRouter()

@router.get(
    "/stats",
    response_model=Stats,
    responses={
        404: {"model": ErrorResponse, "description": "Статистика не найдена"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос"}
    }
)
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
    

@router.get(
    "/me", 
    response_model=UserReturn,
    responses={
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос"},
    }
)
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
    

@router.patch(
    "/change-me",
    response_model=UserUpdatedInfo,
    responses={
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос"},
    }
)   
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


@router.post(
    "/change-avatar",
    response_model=UserChangeAvatar,
    responses={
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос"},
    }
)
async def change_avatar(
    file: UploadFile = File(...),
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.change_avatar(int(current_user), file)
    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.delete(
    "/delete-me",
    response_model=MessageReturn,
    responses={
        400: {"model": ErrorResponse, "description": "Некорректный запрос"}
    }
)
async def soft_delete(
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.soft_delete_account(int(current_user)) 
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get(
    "/course",
    response_model=UserCourseResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Курс не найден"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос"},
    }
)
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
    

@router.get(
    "/course-stat",
    response_model=list[UserCourseProgressReturn],
    responses={
        404: {"model": ErrorResponse, "description": "Информация о курсах не найдена"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос"},
    }
)
async def get_user_course_stat(
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.get_user_course_progress(int(current_user))
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация о курсах не найдена"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    
