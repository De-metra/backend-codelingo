from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, conint, model_validator
from typing import Optional, Any
import re



class Task(BaseModel):
    id: int
    title: str
    description: str
    task_type: int
    hint: str | None = None





class TaskAnswer(BaseModel):
    answers: Any

