from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, conint, model_validator, ConfigDict
from typing import Optional, Any
import re


class UserBase(BaseModel):
    """Базовая модель пользователя"""
    username: str = Field(..., min_length=2, max_length=50, example="Робо-кот")
    email: EmailStr = Field(..., example="codelingo@example.com")

class UserLogin(BaseModel):
    """Модель для входа (логина)"""
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=5, max_length=50, example="mypassword123")

class UserRegister(UserBase):
    """Модель для регистрации пользователя"""
    password: str = Field(..., min_length=5, max_length=50, example="mypassword123")

class UserReturn(UserBase):
    """Модель для регистрации пользователя"""
    id: int
    picture_link: Optional[str]
    xp: Optional[int] = 0
    streak: Optional[int] = 0

class UserPrivateInfo(BaseModel):
    password: str
    created_at: datetime
    #last_login: datetime

class UserChangeProfile(BaseModel):
    username: Optional[str] = None
    picture_link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdatedInfo(BaseModel):
    id: int
    email: EmailStr
    username: str
    picture_link: Optional[str]

class UserChangePassword(BaseModel):
    password: str = Field(..., min_length=5, max_length=50, example="mypassword123")

#model_config = ConfigDict(from_attributes=True)

class Stats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    last_activity: Optional[datetime] = None
    streak: int
    total_xp: int