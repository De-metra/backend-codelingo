class AppError(Exception):
    """Базовая ошибка приложения"""

class NotFoundError(AppError):
    pass


class AlreadyExistsError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ValidationError(AppError):
    pass


class UserNotFoundError(AppError):
    pass

class LevelNotFoundError(AppError):
    pass

class CourseNotFoundError(AppError):
    pass

class TaskNotFoundError(AppError):
    pass

class TheoryNotFoundError(AppError):
    pass

class XpNotFoundError(AppError):
    pass

class StatsNotFoundError(AppError):
    pass

class AchievmentNotFoundError(AppError):
    pass


class LevelAlreadyCompletedError(AppError):
    pass

class UserAlreadyExistsError(AppError):
    pass

class CourseAlreadyStartedError(AppError):
    pass


class InvalidCodeError(AppError):
    pass

class NoneDataToUpdate(AppError):
    pass