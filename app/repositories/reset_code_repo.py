from datetime import datetime

from app.repositories.base import Repository
from app.models.models import PasswordResetCode
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload
from app.core.security import verify_password, get_password_hash


class ResetCodeRepository(Repository):  
    model = PasswordResetCode

    async def create(self, user_id: int, code: str, expires_at: datetime):
        reset_code = PasswordResetCode(
            user_id=user_id,
            code=code,
            expires_at=expires_at,
            is_used=False,
        )
        self.session.add(reset_code)
        return reset_code
    
    async def add(self, data: PasswordResetCode):
        self.session.add(data)
        

    async def get_valid_code(self, user_id: int, code: str):
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


    async def mark_used(self, reset_code: PasswordResetCode):
        reset_code.is_used = True