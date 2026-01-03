from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, conint, model_validator
from typing import Optional, Any
import re
from app.schemas.schemas import Task

class LevelStatusReturn(BaseModel):
    id: int
    title: str
    is_complete: bool

class LevelBaseReturn(BaseModel):
    id: int
    title: str
    description: str | None
    is_complete: bool

class LevelReturn(LevelStatusReturn):
    description: str
    theory: str
    xp: int
    tasks: list[Task]

class TheoryReturn(BaseModel):
    theory: str