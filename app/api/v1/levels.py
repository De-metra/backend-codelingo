from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.level import LevelBaseReturn, TheoryReturn
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

@router.get("/{level_id}/", response_model=LevelBaseReturn)
async def get_level_info(level_id: int, current_user: str = Depends(get_user_from_token), level_service: LevelService = Depends(get_level_service)):
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


@router.get("/{level_id}/theory/", response_model=TheoryReturn)
async def get_level_info(level_id: int, level_service: LevelService = Depends(get_level_service)):
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


@router.get("/{level_id}/xp/") 
async def get_xp(level_id: int, level_service: LevelService = Depends(get_level_service)):
 
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
    

@router.post("/{level_id}/complete/")
async def complete_level(
    level_id: int, 
    current_user: str = Depends(get_user_from_token), 
    level_service: LevelService = Depends(get_level_service)
):
    """
    Docstring for complete_level
    
    :param level_id: Description
    :type level_id: int
    :param current_user: Description
    :type current_user: str
    :param level_service: Description
    :type level_service: LevelService

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

    
@router.get("/{level_id}/tasks/")
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

