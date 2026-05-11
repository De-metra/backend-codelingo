from datetime import datetime, timedelta

from fastapi import UploadFile

from app.core.cloudinary import upload_image
from app.schemas.schemas import MessageReturn
from app.schemas.course import UserCourseProgressReturn, UserCourseResponse
from app.schemas.user import UserRegister, UserReturn, Stats, UserUpdatedInfo, UserChangeAvatar
from app.models.models import Users, Users_Stats
from app.utils.uow import IUnitOfWork
from app.core.exception import NotFoundError, StatsNotFoundError, UserNotFoundError, NoneDataToUpdate


class UserService():
    def __init__(self, uow: IUnitOfWork):
        self.uow : IUnitOfWork = uow

    async def add_user(self, user: UserRegister) -> UserReturn:
        user_dict: dict = user.model_dump()

        async with self.uow:     
            user_from_db = await self.uow.user.add(user_data=Users(**user_dict)) 
            user_to_return = UserReturn.model_validate(user_from_db)

            await self.uow.commit()

            return user_to_return
        

    async def get_users(self) -> list[UserReturn]:
        async with self.uow:
            users = await self.uow.user.find_all()
            return [UserReturn.model_validate(user) for user in users]


    async def get_user_stats(self, user_id: int) -> Stats:
        async with self.uow:
            stats = await self.uow.user_stats.find_one_or_none(user_id=user_id)

            if not stats:
                raise StatsNotFoundError()
            
            return Stats.model_validate(stats)
        
    async def get_user_with_stats(self, user_id: int) -> UserReturn:
        async with self.uow:
            user = await self.uow.user.get_user_with_stats(user_id=user_id)

            if not user:
                raise UserNotFoundError()
            
            if not user.stats:
                stats = Users_Stats(user_id=user.id, total_xp=0, streak=0)
                await self.uow.user_stats.add(stats)
                await self.uow.commit()
            else:
                stats = await self._refresh_streak_status(user.stats)

            return UserReturn(
                id=user.id,
                username=user.username,
                email=user.email,
                picture_link=user.picture_link,
                xp=stats.total_xp,
                streak=stats.streak
            )
        
    async def change_avatar(self, user_id: int, file: UploadFile) -> UserChangeAvatar:
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()

            avatar_url = upload_image(file=file.file, user_id=user_id) 

            user.picture_link = avatar_url
            await self.uow.commit()

            return UserChangeAvatar(avatar_url=avatar_url)
        
    
    async def change_me(self, user_id: int, username: str | None, file: UploadFile | None) -> UserUpdatedInfo:
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()
            
            update_data = {}

            if username:
                update_data["username"] = username

            if file:
                picture_link = upload_image(file=file.file, user_id=user_id) 
                update_data["picture_link"] = picture_link   

            if not update_data:
                raise NoneDataToUpdate()

            await self.uow.user.update(user, update_data)
            await self.uow.commit()

            return UserUpdatedInfo(
                id=user_id,
                username=user.username,
                email=user.email, 
                picture_link=user.picture_link
            )

        
    async def soft_delete_account(self, user_id: int) -> MessageReturn:
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()
            
            user.is_active = False
            user.deleted_at = datetime.now()

            await self.uow.commit()

            return MessageReturn(message=f"Аккаунт {user.username} успешно удалён")
        

    async def get_user_course(self, user_id: int) -> UserCourseResponse:
        async with self.uow:
            user_course = await self.uow.user_course.get_last_active_course(user_id)

            if not user_course:
                return UserCourseResponse(course_id=None, course_title=None, course_icon=None) 
            
            return UserCourseResponse(course_id=user_course.course_id, course_title=user_course.course.title, course_icon=user_course.course.icon)
        

    async def get_user_course_progress(self, user_id: int) -> list[UserCourseProgressReturn]:
        async with self.uow:
            user_courses = await self.uow.user_course.get_progress_of_courses(user_id)

            if not user_courses:
                raise NotFoundError()
            
            return [
                UserCourseProgressReturn(
                    id=u_c.id,
                    course_name=u_c.course.title,
                    course_icon=u_c.course.icon,
                    progress=u_c.progress,
                    is_complete=u_c.is_complete,
                    started_at=u_c.started_at
                )
                for u_c in user_courses
            ]
        
    async def _refresh_streak_status(self, stats: Users_Stats) -> Users_Stats:
        now = datetime.now().date()
        if not stats.last_activity:
            return stats

        last_activity_date = stats.last_activity.date()
        
        if last_activity_date < now - timedelta(days=1):
            stats.streak = 0
    
        return stats