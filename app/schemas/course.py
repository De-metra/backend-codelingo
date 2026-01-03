from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, conint, model_validator, ConfigDict
from typing import Optional, Any
import re

class LevelBase(BaseModel):
    id: int
    title: str
    xp: int

class CourseReturn(BaseModel):
    id: int 
    title: str
    description: Optional[str] 

    model_config = ConfigDict(from_attributes=True)

class CourseWithLevels(CourseReturn):
    levels: list[LevelBase]




