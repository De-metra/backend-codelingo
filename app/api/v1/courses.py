from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.level import LevelStatusReturn
from app.schemas.course import CourseReturn, CourseWithLevels
from app.schemas.schemas import MessageReturn, ErrorResponse
from app.core.security import get_user_from_token
from app.utils.dependencies import get_level_service, get_course_service
from app.services.course_service import CourseService
from app.services.level_service import LevelService
from app.core.exception import (
    AppError, AlreadyExistsError,
    LevelNotFoundError, NotFoundError
)


router = APIRouter()

@router.get("/", response_model=list[CourseReturn])
async def get_courses(course_service: CourseService = Depends(get_course_service)):
    return await course_service.get_all_courses()


@router.get(
    "/{course_id}",
    response_model=CourseWithLevels,
    responses={
        404: {"model": ErrorResponse, "description": "Курс не найден"}
    }
)
async def get_course_with_levels(
    course_id: int, 
    course_servise: CourseService = Depends(get_course_service)
):
    try:
        return await course_servise.get_course_with_levels(course_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Курс не найден")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get(
    "/{course_id}/levels",
    response_model=list[LevelStatusReturn],
    responses={
        404: {"model": ErrorResponse, "description": "Курс или уровни не найдены"}
    }
)
async def get_levels(
    course_id: int, 
    current_user: str = Depends(get_user_from_token), 
    level_service: LevelService = Depends(get_level_service)):
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
    

@router.post(
    "/{course_id}/start",
    response_model=MessageReturn,
    responses={
        400: {"model": ErrorResponse, "description": "Курс уже начат"},
        404: {"model": ErrorResponse, "description": "Курс не найден"}
    }
)
async def start_course(
    course_id: int, 
    current_user: str = Depends(get_user_from_token), 
    course_service: CourseService = Depends(get_course_service)
):
    try:
        return await course_service.start_course(course_id=course_id, user_id=int(current_user))
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Курс не найден")
    except AlreadyExistsError:
        raise HTTPException(status_code=400, detail="Курс уже начат") 
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err 
