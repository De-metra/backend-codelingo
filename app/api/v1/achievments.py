from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserReturn, UserChangeProfile
from app.core.security import  get_user_from_token
from app.services.achievment_service import AchievmentsService
from app.utils.dependencies import get_achievment_service
from app.core.exception import (
    AppError, StatsNotFoundError,
    UserNotFoundError, NoneDataToUpdate
)


router = APIRouter()

@router.post("/check") 
async def check_achievments(
    current_user: str = Depends(get_user_from_token),
    achiv_service: AchievmentsService = Depends(get_achievment_service)
):
    try:
        return await achiv_service.check_after_level_complete(int(current_user))
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err    

@router.get("/my") 
async def get_my_achievments(
    current_user: str = Depends(get_user_from_token),
    achiv_service: AchievmentsService = Depends(get_achievment_service)
):
    try:
        return await achiv_service.get_all_with_status(int(current_user))
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err    