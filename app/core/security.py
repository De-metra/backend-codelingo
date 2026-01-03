import random
from typing import Dict
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException

from app.core.config import get_auth_data


# OAuth2PasswordBearer извлекает токен из заголовка "Authorization: Bearer <token>"
# Параметр tokenUrl указывает маршрут, по которому клиенты смогут получить токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#SECRET_KEY = os.getenv("SECRET_KEY", "codelingo_secret")  # В реальной практике генерируйте ключ, например, с помощью 'openssl rand -hex 32', и храните его в безопасности
#ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*365  # Время жизни токена

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Функция для создания JWT токена с заданным временем жизни
def create_jwt_token(data: Dict, expires_delta: timedelta = None):
    """
    Функция для создания JWT токена. Мы копируем входные данные, добавляем время истечения и кодируем токен.
    """
    to_encode = data.copy()  # Копируем данные, чтобы не изменить исходный словарь
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))  # Задаем время истечения токена
    to_encode.update({"exp": expire})  # Добавляем время истечения в данные токена
    auth_data = get_auth_data()
    return jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])  # Кодируем токен с использованием секретного ключа и алгоритма


# Функция для получения пользователя из токена
def get_user_from_token(token: str = Depends(oauth2_scheme)):       #ПОДУМАТЬ НАДО ЛИ ВОЗВРАЩАТЬ ЦЕЛОГО ПОЛЬЗОВАТЕЛЯ
    """
    Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе.
    """
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])  # Декодируем токен с помощью секретного ключа
        return payload.get("sub")  # Возвращаем утверждение о пользователе (subject) из полезной нагрузки
    except JWTError:
        raise HTTPException(status_code=401, detail='Токен не валидный!')

CODE_LENGTH = 6

def generate_reset_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(CODE_LENGTH)])

def create_reset_code(user_id: int, ):
    pass
    