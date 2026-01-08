import logging

from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from jose import jwt

from app.core.security import create_jwt_token, get_user_from_token
from app.models.models import (
    Courses, Users, Users_Stats, 
    Users_Courses, Users_Levels, Levels, Theories, Level_Tasks, 
    Tasks, Tasks_Types, Tests, Data_Types, Tasks_Options, Tasks_Gap, 
    PasswordResetCode, Achievments, Users_Achievments
)


logger = logging.getLogger('admin_actions')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('admin_actions.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

#форматтер
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class LoggingMixin:

    async def _log_action(self, action: str, model_name: str, object_id: str = None, details: str = ""):
        """Логирование действия"""
        log_message = f"ADMIN_ACTION - {action} - Model: {model_name}"
        if object_id:
            log_message += f" - ID: {object_id}"
        if details:
            log_message += f" - Details: {details}"

        logger.info(log_message)

    async def after_model_change(self, form, model, is_created, request):
        """После создания/изменения модели"""
        action = "CREATE" if is_created else "UPDATE"

        form_data = form.data if hasattr(form, "data") else form

        await self._log_action(
            action=action,
            model_name=self.model.__name__,
            object_id=str(model.id) if hasattr(model, 'id') else "unknown",
            details=f"Form data: {form_data}"
        )
        return await super().after_model_change(form, model, is_created, request)
    
    async def after_model_delete(self, model, request):
        """После удаления модели"""
        await self._log_action(
            action="DELETE",
            model_name=self.model.__name__,
            object_id=str(model.id) if hasattr(model, 'id') else "unknown"
        )
        return await super().after_model_delete(model, request)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

                
        if username == "admin_codelingo_super" and password == "backend-codelingo":     #проверку заменить на что-то другое
            token = create_jwt_token({"sub": username})

            request.session.update({"token": token})
            return True
        
        return False
    
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token: 
            return False
        
        try: 
            username = get_user_from_token(token)
            return username == "admin_codelingo_super"
        except jwt.JWTError:
            return False


class CustomTextAreaField(TextAreaField):
    """Кастомное текстовое поле с настройками"""
    widget = TextArea()

class PasswordResetAdmin(LoggingMixin, ModelView, model=PasswordResetCode):
    column_list = [PasswordResetCode.id, PasswordResetCode.user, PasswordResetCode.is_used, PasswordResetCode.expires_at]
    name = "Reset Code"
    name_plural = "Reset Codes"

    form_excluded_columns = [PasswordResetCode.updated_at, PasswordResetCode.user, PasswordResetCode.code]

    column_sortable_list = [PasswordResetCode.expires_at]

class CourseAdmin(LoggingMixin, ModelView, model=Courses):
    column_list = [Courses.id, Courses.title, Courses.description, Courses.updated_at, Courses.levels]
    name = "Course"
    name_plural = "Courses"
    icon = "fa-solid fa-layer-group"

    form_excluded_columns = [Courses.updated_at, Courses.levels, Courses.user_courses]

    form_overrides = {
        "description": CustomTextAreaField
    }
    
    form_widget_args = {
        'description': {
            'rows': 10,      
            'style': 'width: 100%',  
            'class': 'form-control' 
        }
    }

    column_formatters = {
        Courses.description: lambda m, a: (
            m.description[:40] + "..." if m.description and len(m.description) > 40
            else m.description or ""
        )
    }

    column_searchable_list = [Courses.title]
    column_sortable_list = [Courses.id]

class AchievmentsAdmin(LoggingMixin, ModelView, model=Achievments):
    column_list = [Achievments.id, Achievments.code, Achievments.title, Achievments.description, Achievments.icon, Achievments.updated_at]
    name = "Achievment"
    name_plural = "Achievments"

    form_excluded_columns = [Achievments.updated_at, Achievments.user_achievments]
    column_searchable_list = [Achievments.title]

class UserAdmin(LoggingMixin, ModelView, model=Users):
    column_list = [Users.id, Users.username, Users.email, Users.picture_link, Users.created_at, Users.updated_at]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    form_excluded_columns = [Users.hashed_password, Users.updated_at, Users.created_at, Users.stats, Users.levels, Users.courses, Users.achievments]
    form_ajax_refs = {
        "stats" : {
            "fields": ("id", "user_id"),
            "order_by": ("id")
        },
        "levels" : {
            "fields": ("id", "user_id"),
            "order_by": ("id")
        }
    }

    column_searchable_list = [Users.username, Users.email]
    column_sortable_list = [Users.created_at, Users.username]
    column_default_sort = [(Users.created_at, False)]

class UsersStatsAdmin(LoggingMixin, ModelView, model=Users_Stats):        #last-activity убрать или нет
    column_list = "__all__"
    #column_exclude_list = [Users_Stats.user]
    name = "User Stat"
    name_plural = "User Stats"
    icon = "fa-solid fa-users"

    form_excluded_columns = [Users_Stats.updated_at]
    form_ajax_refs = {
        "user" : {
            "fields": (Users.username, Users.email),
            "order_by": "username"
        }
    }

    column_searchable_list = [Users_Levels.user_id]
    column_sortable_list = [Users_Stats.last_activity, Users_Stats.streak, Users_Stats.total_xp]
    column_default_sort = [(Users_Stats.total_xp, True)]

class UsersAchievmentsAdmin(LoggingMixin, ModelView, model=Users_Achievments):
    column_list = "__all__"
    name = "User Achievment"
    name_plural = "User Achievments"

    form_excluded_columns = [Users_Achievments.updated_at, Users_Achievments.received_at]
    column_searchable_list = [Users_Achievments.user_id]
    column_sortable_list = [Users_Achievments.user_id, Users_Achievments.achievment_id]

class UsersCoursesAdmin(LoggingMixin, ModelView, model=Users_Courses):
    column_list = "__all__"
    name = "User Course"
    name_plural = "User Courses"

    form_excluded_columns = [Users_Courses.updated_at, Users_Courses.started_at]
    column_searchable_list = [Users_Courses.user_id]

class UsersLevelsAdmin(LoggingMixin, ModelView, model=Users_Levels):
    column_list = "__all__"
    #column_exclude_list = [Users_Levels.user, Users_Levels.level]
    name = "User Level"
    name_plural = "User Levels"

    form_excluded_columns = [Users_Levels.updated_at]

    column_searchable_list = [Users_Levels.user_id]

class LevelAdmin(LoggingMixin, ModelView, model=Levels):
    #column_list = "__all__"
    column_exclude_list = [Levels.user_levels]
    name = "Level"
    name_plural = "Levels"

    form_excluded_columns = [Levels.updated_at, Levels.tasks, Levels.user_levels]
    form_ajax_refs = {
    }
    #form_columns = [Levels.title, Levels.description, Levels.theory, Levels.xp]

    form_overrides = {
        "description": CustomTextAreaField
    }
    
    form_widget_args = {
        'description': {
            'rows': 10,      # Количество строк
            'style': 'width: 100%',  # Ширина
            'class': 'form-control'  # CSS класс
        }
    }

    column_formatters = {
        Levels.description: lambda m, a: (
            m.description[:40] + "..." if m.description and len(m.description) > 40
            else m.description or ""
        )
    }

    column_searchable_list = [Levels.title]
    column_sortable_list = [Levels.id, Levels.xp]

class TheoryAdmin(LoggingMixin, ModelView, model=Theories):           #многострочное деск
    column_list = "__all__"
    name = "Theory"
    name_plural = "Theories"

    form_excluded_columns = [Theories.updated_at, Theories.levels]
    form_overrides = {
        "description": CustomTextAreaField
    }
    
    form_widget_args = {
        'description': {
            'rows': 10,      # Количество строк
            'style': 'width: 100%',  # Ширина
            'class': 'form-control'  # CSS класс
        }
    }

    column_formatters = {
        Theories.description: lambda m, a: (
            m.description[:100] + "..." if m.description and len(m.description) > 100
            else m.description or ""
        )
    }

    column_searchable_list = [Theories.description]

class LevelTaskAdmin(LoggingMixin, ModelView, model=Level_Tasks):
    column_list = "__all__"
    name = "Level Task"
    name_plural = "Level Tasks"

    form_excluded_columns = [Level_Tasks.updated_at]

    column_searchable_list = [Level_Tasks.level_id]
    column_sortable_list = [Level_Tasks.level_id, Level_Tasks.num_in_order]


class TaskAdmin(LoggingMixin, ModelView, model=Tasks):
    column_list = [Tasks.id, Tasks.title, Tasks.description, Tasks.type_rel, Tasks.hint, Tasks.template, Tasks.func_name, Tasks.updated_at]
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-code"

    form_excluded_columns = [Tasks.updated_at, Tasks.tasks_link, Tasks.tests, Tasks.options, Tasks.gaps]
    column_formatters = {
        Tasks.description: lambda m, a: (
            m.description[:40] + "..." if m.description and len(m.description) > 40
            else m.description or ""
        )
    }

    form_overrides = {
        "template": CustomTextAreaField
    }
    
    form_widget_args = {
        'description': {
            'rows': 5,      # Количество строк
            'style': 'width: 100%',  # Ширина
            'class': 'form-control'  # CSS класс
        }
    }

    column_searchable_list = [Tasks.title, Tasks.description]
    column_sortable_list = [Tasks.id, Tasks.task_type]
    

class TaskTypeAdmin(LoggingMixin, ModelView, model=Tasks_Types):
    column_list = [Tasks_Types.id, Tasks_Types.name]
    name = "Task Type"
    name_plural = "Task Types"
    icon = "fa-solid fa-list"

    form_excluded_columns = [Tasks_Types.updated_at, Tasks_Types.tasks]     #хз что в тестах

class TestAdmin(LoggingMixin, ModelView, model=Tests):
    column_list = "__all__"
    name = "Test"
    name_plural = "Tests"

    form_excluded_columns = [Tests.updated_at]

    column_searchable_list = [Tests.input_data, Tests.expected_output_data]

class DataTypeAdmin(LoggingMixin, ModelView, model=Data_Types):
    column_list = "__all__"
    name = "Data Type"
    name_plural = "Data Types"

    form_excluded_columns = [Data_Types.updated_at]

class TaskOptionAdmin(LoggingMixin, ModelView, model=Tasks_Options):
    column_list = "__all__"
    name = "Task Choice"
    name_plural = "Task Choices"

    form_excluded_columns = [Tasks_Options.updated_at]

    column_searchable_list = [Tasks_Options.task_id]
    column_formatters = {
        Tasks_Options.text: lambda m, a: (
            m.text[:40] + "..." if m.text and len(m.text) > 40
            else m.text or ""
        )
    }

    column_searchable_list = [Tasks_Options.text]

class TaskGapAdmin(LoggingMixin, ModelView, model=Tasks_Gap):
    column_list = "__all__"
    name = "Task Gap"
    name_plural = "Task Gaps"

    form_excluded_columns = [Tasks_Gap.updated_at]
    column_formatters = {
        Tasks_Gap.template: lambda m, a: (
            m.template[:40] + "..." if m.template and len(m.template) > 40
            else m.template or ""
        )
    }

    form_overrides = {
        "template": CustomTextAreaField
    }
    
    form_widget_args = {
        'template': {
            'rows': 3,      # Количество строк
            'style': 'width: 100%',  # Ширина
            'class': 'form-control'  # CSS класс
        }
    }

    column_searchable_list = [Tasks_Gap.template, Tasks_Gap.answer]