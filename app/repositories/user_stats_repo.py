from sqlalchemy import select

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Users_Stats


class UserStatsRepository(SQLAlchemyRepository):  
    model = Users_Stats

    async def add(self, data: Users_Stats) -> Users_Stats:
        self.session.add(data)
        return data
    
    async def get_or_create(self, user_id: int) -> Users_Stats:
        stmt = await self.session.execute(
            select(Users_Stats)
            .where(Users_Stats.user_id == user_id))
        stats = stmt.scalar_one_or_none()

        if not stats:
            stats = Users_Stats(
                user_id=user_id,
                total_xp=0,
                streak=0
            )
            self.session.add(stats)
        
        return stats

