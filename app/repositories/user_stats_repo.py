from app.repositories.base import Repository
from app.models.models import Users_Stats
from sqlalchemy import select, update, and_, insert


class UserStatsRepository(Repository):  
    model = Users_Stats

    async def add(self, data: Users_Stats):
        self.session.add(data)
        return data
    
    async def get_user_stats(self, user_id: int):
        stmt = await self.session.execute(
            select(Users_Stats)
            .where(Users_Stats.user_id == user_id))
        return stmt.scalars().first()
    
    async def get_or_create(self, user_id: int):
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

