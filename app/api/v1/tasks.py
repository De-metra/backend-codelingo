from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.schemas import TaskAnswer
from app.core.security import  get_user_from_token
from app.services.task_service import TaskService
from app.utils.dependencies import get_task_service
from app.core.exception import AppError, TaskNotFoundError


router = APIRouter()

@router.get("/{task_id}")
async def get_task_info(
    task_id: int, 
    task_service: TaskService = Depends(get_task_service)
):
    try:
        return await task_service.get_task_by_id(task_id=task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Задача не найдены")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.get("/{task_id}/hint")
async def get_level_info(
    task_id: int, 
    task_service: TaskService = Depends(get_task_service)
):
    """
    Возвращает подсказку задачи.
    """
    try:
        return await task_service.get_task_hint(task_id=task_id)
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post("/{task_id}/submit")           # ДОПИСАТЬ
async def check_task_answer(
    task_id : int, 
    answer_data : TaskAnswer, 
    current_user: str = Depends(get_user_from_token), 
    task_service : TaskService = Depends(get_task_service)
):
    try:
        return await task_service.submit_task(
            task_id=task_id, 
            user_id=int(current_user),
            answer_data=answer_data
            )
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err

    







