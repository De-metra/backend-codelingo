from typing import Optional, Any

from pydantic import BaseModel


class TaskType(BaseModel):
    ...

class TaskOption(TaskType):
    id: int
    text: str

class TaskGap(TaskType):
    template: str

class TaskCode(TaskType):
    id: int
    func_name: str | None = None
    template: str | None = None 
    language: str 


class TaskBase(BaseModel):
    id: int
    title: str
    description: str | None
    task_type: str
    num_in_order: int
    hint: str | None


class AllTasksReturn(TaskBase):
    options: Optional[list[TaskOption]] = None
    gaps: Optional[list[TaskGap]] = None
    code: Optional[list[TaskCode]] = None

class TaskAnswer(BaseModel):
    answers: Any

class TaskHintReturn(BaseModel):
    hint: Optional[str] = None