from typing import Optional

from pydantic import BaseModel


class AchievmentReturn(BaseModel):
    id: int
    title: str
    icon: Optional[str] = None

class AchievmentWithStatusReturn(AchievmentReturn):
    description: Optional[str] = None
    received: bool = False