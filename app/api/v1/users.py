from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserReturn, UserChangeProfile
from app.core.security import  get_user_from_token
from app.services.user_service import UserService
from app.utils.dependencies import get_user_service
from app.core.exception import (
    AppError, StatsNotFoundError,
    UserNotFoundError, NoneDataToUpdate
)


router = APIRouter()

@router.get("/stats/")
async def get_users_stats(
    current_user: str = Depends(get_user_from_token), 
    user_service: UserService = Depends(get_user_service)
):
    '''Получаем статистику конкретного пользователя.'''
    try:
        return await user_service.get_user_stats(int(current_user))
    except StatsNotFoundError: 
        raise HTTPException(status_code=404, detail="Статистика не найдена")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get("/me", response_model=UserReturn)
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
    
    
@router.post("/change-me")      
async def change_profile(
    users_data : UserChangeProfile, 
    current_user: str = Depends(get_user_from_token), 
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.change_me(user_id=int(current_user), data=users_data)
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


@router.get("/achievments")
async def get_my_achievments(
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        pass
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err    