from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.level import LevelStatusReturn, LevelReturn
from app.schemas.course import CourseReturn
from app.core.security import get_user_from_token
from app.utils.dependencies import get_level_service, get_course_service
from app.services.course_service import CourseService
from app.services.level_service import LevelService
from app.core.exception import (
    AppError, CourseNotFoundError, 
    LevelNotFoundError, CourseAlreadyStartedError
)


router = APIRouter()

@router.get("/", response_model=list[CourseReturn])
async def get_courses(course_service: CourseService = Depends(get_course_service)):
    return await course_service.get_all_courses()

@router.get("/{course_id}/")
async def get_course_with_levels(
    course_id: int, 
    course_servise: CourseService = Depends(get_course_service)
):
    try:
        return await course_servise.get_course_with_levels(course_id)
    except CourseNotFoundError:
        raise HTTPException(status_code=404, detail="Курс не найден")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get("/{course_id}/levels")
async def get_levels(
    course_id: int, 
    current_user: str = Depends(get_user_from_token), 
    level_service: LevelService = Depends(get_level_service)) -> list[LevelStatusReturn]:
    """
    Возвращает список всех уровней и состояние (пройден / не пройден) для текущего пользователя.
    """
    try:
        return await level_service.get_levels_with_progress(course_id, int(current_user))
    except LevelNotFoundError:
        raise HTTPException(status_code=404, detail="Уровни не найдены")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.post("/{course_id}/start")
async def start_course(
    course_id: int, 
    current_user: str = Depends(get_user_from_token), 
    course_service: CourseService = Depends(get_course_service)
):
    try:
        return await course_service.start_course(course_id=course_id, user_id=int(current_user))
    except CourseNotFoundError:
        raise HTTPException(status_code=404, detail="Курс не найден")
    except CourseAlreadyStartedError:
        raise HTTPException(status_code=400, detail="Курс уже начат") 
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err 
