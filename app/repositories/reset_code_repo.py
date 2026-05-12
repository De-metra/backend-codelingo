from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select, and_

from app.repositories.base import SQLAlchemyRepository
from app.models.models import PasswordResetCode


class ResetCodeRepository(SQLAlchemyRepository):
    model = PasswordResetCode
    
    async def add(self, data: PasswordResetCode) -> PasswordResetCode:
        self.session.add(data)
        return data
        
    async def get_existing_code(self, user_id: int) -> Optional[PasswordResetCode]:
        stmt = await self.session.execute(
            select(PasswordResetCode).where(
                and_(
                    PasswordResetCode.user_id == user_id,
                    PasswordResetCode.is_used == False,
                    PasswordResetCode.expires_at > datetime.now()
                ) 
            )
        )
        return stmt.scalar_one_or_none()

    async def get_valid_code(self, user_id: int, code: str) -> Optional[PasswordResetCode]:
        stmt = select(PasswordResetCode).where(
            and_(
                PasswordResetCode.user_id == user_id,
                PasswordResetCode.code == code,
                PasswordResetCode.is_used == False,
                PasswordResetCode.expires_at > datetime.now(),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_by_user_id(self, user_id: int):
        stmt = delete(PasswordResetCode).where(
        PasswordResetCode.user_id == user_id
    )
        await self.session.execute(stmt)