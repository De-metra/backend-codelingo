from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.api.v1 import auth, levels, tasks, courses, users, achievments
from app.core.config import get_admin_key
from app.database.db import engine
from app.internal.admin_views import (
    AdminAuth, CourseAdmin, 
    UserAdmin, UsersStatsAdmin, UsersCoursesAdmin, 
    UsersLevelsAdmin, LevelAdmin, TheoryAdmin, 
    LevelTaskAdmin, TaskAdmin, TaskTypeAdmin, 
    TaskOptionAdmin, TaskGapAdmin, TestAdmin, 
    DataTypeAdmin, PasswordResetAdmin, AchievmentsAdmin, UsersAchievmentsAdmin,
)


app = FastAPI(title="CodeLingo API")

data_key = get_admin_key()
authentication_backend = AdminAuth(secret_key=data_key['secret_key'])   
admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(UsersStatsAdmin)
admin.add_view(UsersAchievmentsAdmin)
admin.add_view(UsersCoursesAdmin)
admin.add_view(UsersLevelsAdmin)
admin.add_view(AchievmentsAdmin)
admin.add_view(CourseAdmin)
admin.add_view(LevelAdmin)
admin.add_view(TheoryAdmin)
admin.add_view(LevelTaskAdmin)
admin.add_view(TaskAdmin)
admin.add_view(TaskTypeAdmin)
admin.add_view(TaskOptionAdmin)
admin.add_view(TaskGapAdmin)
admin.add_view(TestAdmin)
admin.add_view(DataTypeAdmin)
admin.add_view(PasswordResetAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(levels.router, prefix="/api/levels", tags=["levels"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(achievments.router, prefix="/api/achievments", tags=["achievments"])

@app.get("/")
async def get_root():
    return {"message": "Hello World"}
