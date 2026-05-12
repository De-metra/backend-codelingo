from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.schemas.auth import TokenReturn
from app.schemas.schemas import ErrorResponse, MessageReturn
from app.schemas.user import UserLogin, UserRegister
from app.schemas.email import  EmailRequest, CodeRequest, CodeUpdateRequest
from app.services.auth_service import AuthService
from app.utils.dependencies import get_auth_service
from app.core.exception import (
    AppError, UserAlreadyExistsError, UnauthorizedError,
    UserNotFoundError, InvalidCodeError, GoogleAuthError
)
from app.core.oath_google import generate_google_oath_redirect_uri
from app.core.config import settings


router = APIRouter()


@router.get(
    "/google/login",
    status_code=status.HTTP_302_FOUND,
    description="Перенаправляет пользователя на страницу авторизации Google"    
)
async def get_google_auth_redirect_uri(platform: str = "mobile"):
   uri = generate_google_oath_redirect_uri(platform=platform)
   print(uri)
   return RedirectResponse(url=uri, status_code=302)


@router.get(
    "/google/callback",
    status_code=status.HTTP_302_FOUND,
    responses={400: {"model": ErrorResponse, "description": "Ошибка при аутентификации через Google"}},
    description="Обрабатывает callback от Google после авторизации пользователя"
)
async def handle_code(
    code: str,
    state: str = "mobile",
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        jwt_token = await auth_service.google_callback(code)

        if state == "mobile":
            redirect_base_url = settings.MOBILE_APP_REDIRECT_URL
        else:
            redirect_base_url = settings.WEB_APP_REDIRECT_URL
        return RedirectResponse(url=f"{redirect_base_url}?access_token={jwt_token}")   
    except GoogleAuthError:
        raise HTTPException(status_code=400, detail="Ошибка при аутентификации через Google")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.post(
    "/register",
    response_model=MessageReturn,
    responses={
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"},
        409: {"model": ErrorResponse, "description": "Email уже зарегистрирован"} 
    }
)
async def register(
    user_in: UserRegister, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.register(user_in)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=409, 
            detail="Email уже зарегистрирован"
        )
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    
@router.post(
    "/verify-email",
    response_model=TokenReturn,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный код"}
    } 
)
async def verify_email(
    data: CodeRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.verify_and_activate(data=data)
    except InvalidCodeError:
        raise HTTPException(status_code=400, detail="Неверный код")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err

    
   
@router.post(
    "/login",
    response_model=TokenReturn,
    responses={
        401: {"model": ErrorResponse, "description": "Неверный логин или пароль"},
        400: {"model": ErrorResponse, "description": "Некорректные данные запроса"} 
    }
)
async def login(
    user_in: UserLogin, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.login(user_in)
    except UnauthorizedError:
        raise HTTPException(
            status_code=401, 
            detail="Неверный логин или пароль"
        ) 
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.post(
    "/forgot-password",
    response_model=MessageReturn,
    responses={400: {"model": ErrorResponse, "description": "Некорректные данные запроса"}},
    description="Отправка кода восстановления на Email (интеграция с Resend)"
)
async def forgot_password(
    user_mail: EmailRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.forgot_password(user_mail=user_mail)
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post(
    "/verify-code",
    response_model=MessageReturn,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный код"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"}
    } 
)
async def verify_code(
    data: CodeRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.verify_code(data=data)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except InvalidCodeError:
        raise HTTPException(status_code=400, detail="Неверный код")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post(
    "/reset-password",
    response_model=MessageReturn,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный код"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"}
    }
)
async def reset_password(
    data: CodeUpdateRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.reset_password(data=data)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except InvalidCodeError:
        raise HTTPException(status_code=400, detail="Неверный код")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
