from app.repositories.base import SQLAlchemyRepository
from app.models.models import Achievments


class AchievmentRepository(SQLAlchemyRepository):  
    model = Achievments
