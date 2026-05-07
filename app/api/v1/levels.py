from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.level import LevelBaseReturn, TheoryReturn, XpReturn, LevelCompleteReturn
from app.schemas.schemas import ErrorResponse
from app.schemas.task import AllTasksReturn
from app.core.security import get_user_from_token
from app.utils.dependencies import get_level_service, get_task_service
from app.services.level_service import LevelService
from app.services.task_service import TaskService
from app.core.exception import (
    AppError, LevelNotFoundError, TheoryNotFoundError,
    XpNotFoundError, UserNotFoundError, 
    LevelAlreadyCompletedError, TaskNotFoundError
)


router = APIRouter()

@router.get(
    "/{level_id}", 
    response_model=LevelBaseReturn,
    responses={
        404: {"model": ErrorResponse, "description": "Уровень не найден"},
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"}
    }
)
async def get_level_info(
    level_id: int, 
    current_user: str = Depends(get_user_from_token), 
    level_service: LevelService = Depends(get_level_service)
):
    """
    Возвращает базовую информацию уровня(id, заголовок, описание, состояние).
    """ 
    try:
        return await level_service.get_level_info(level_id, int(current_user))
    except LevelNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Уровень не найден"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.get(
    "/{level_id}/theory", 
    response_model=TheoryReturn,
    responses={
        404: {"model": ErrorResponse, "description": "Теория не найдена"},
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"}
    }
)
async def get_level_theory(
    level_id: int, 
    level_service: LevelService = Depends(get_level_service)
):
    '''
    Возвращает теорию уровня.
    '''
    try:
        return await level_service.get_level_theory(level_id)
    except TheoryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Теория не найдена"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.get(
    "/{level_id}/xp",
    response_model=XpReturn,
    responses={
        404: {"model": ErrorResponse, "description": "Данные об xp не найдены"},
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"}
    }
) 
async def get_xp(
    level_id: int, 
    level_service: LevelService = Depends(get_level_service)
):
    try:
        return await level_service.get_level_xp(level_id)
    except XpNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Данные об xp не найдены"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.post(
    "/{level_id}/complete",
    response_model=LevelCompleteReturn,
    response_model_exclude_none=True,
    responses={
        404: {"model": ErrorResponse, "description": "Пользователь или уровень не найден/уровень уже завершён"},
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"}
    }
)
async def complete_level(
    level_id: int, 
    current_user: str = Depends(get_user_from_token), 
    level_service: LevelService = Depends(get_level_service)
):
    """
    Начисляется xp, уровень помечается завершенным, обновляется last_activity, streak,
    прогресс курса, проверка на ачивки
    """
    try:
        return await level_service.complete_level(level_id=level_id, user_id=int(current_user))
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except LevelNotFoundError:
        raise HTTPException(status_code=404, detail="Уровень не найден")
    except LevelAlreadyCompletedError:
        raise HTTPException(status_code=404, detail="Уровень уже завершён")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err

    
@router.get(
    "/{level_id}/tasks",
    response_model=list[AllTasksReturn],
    response_model_exclude_none=True,
    responses={
        404: {"model": ErrorResponse, "description": "Уровень или задачи не найдены"},
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"}
    }
)
async def get_level_tasks(
    level_id: int, 
    task_service : TaskService = Depends(get_task_service)
):
    try:
        return await task_service.get_level_tasks(level_id=level_id)
    except LevelNotFoundError:
        raise HTTPException(status_code=404, detail="Уровень не найден")    
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Задачи не найден")    
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err

