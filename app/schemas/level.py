from pydantic import BaseModel

from app.schemas.achiev import AchievmentReturn
from app.schemas.task import TaskBase


class LevelStatusReturn(BaseModel):
    id: int
    title: str
    num_in_order: int
    is_complete: bool

class LevelBaseReturn(BaseModel):
    id: int
    title: str
    description: str | None
    num_in_order: int
    is_complete: bool 

class LevelReturn(LevelStatusReturn):
    description: str
    theory: str
    xp: int
    tasks: list[TaskBase]

class TheoryReturn(BaseModel):
    theory: str

class XpReturn(BaseModel):
    xp: int

class LevelCompleteReturn(BaseModel):
    message: str
    xp_added: int
    total_xp: int
    streak: int
    course_progress: float
    new_achievments: list[AchievmentReturn] | None = None