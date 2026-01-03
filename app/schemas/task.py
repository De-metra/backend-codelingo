from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, conint, model_validator, ConfigDict
from typing import Optional, Any
import re



class TaskType(BaseModel):
    ...

class TaskOption(TaskType):
    id: int
    text: str
    is_correct: bool

class TaskGap(TaskType):
    template: str
    answer: str

class TaskCode(TaskType):
    id: int
    input_data: str
    expected_output_data: str
    input_type: str | None
    output_type: str | None


class TaskBase(BaseModel):
    id: int
    title: str
    description: str | None
    task_type: str
    hint: str | None

    #tasks: list[TaskType]

class TaskAnswer(BaseModel):
    answers: list