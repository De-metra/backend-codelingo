from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LevelBase(BaseModel):
    id: int
    title: str
    xp: int

class CourseReturn(BaseModel):
    id: int 
    title: str
    description: Optional[str] 
    icon: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class UserCourseResponse(BaseModel):
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    course_icon: Optional[str] = None   

class UserCourseProgressReturn(BaseModel):
    id: int
    course_name: str
    course_icon: Optional[str] = None
    progress: float
    is_complete: bool
    started_at: datetime

class CourseWithLevels(CourseReturn):
    levels: list[LevelBase]




