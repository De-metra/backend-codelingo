from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.schemas.user import UserLogin, UserRegister
from app.schemas.email import  EmailRequest, CodeRequest, CodeUpdateRequest
from app.services.auth_service import AuthService
from app.utils.dependencies import get_auth_service
from app.core.exception import (
    AppError, UserAlreadyExistsError, UnauthorizedError,
    UserNotFoundError, InvalidCodeError
)
from app.core.oath_google import generate_google_oath_redirect_uri
from app.core.config import settings


router = APIRouter()


@router.get("/google/login")
async def get_google_auth_redirect_uri():
   uri = generate_google_oath_redirect_uri()
   return RedirectResponse(url=uri, status_code=302)


@router.get("/google/callback")
async def handle_code(
    code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        jwt_token = await auth_service.google_callback(code)
        return RedirectResponse(url=f"{settings.MOBILE_APP_REDIRECT_URL}?access_token={jwt_token}")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err
    

@router.post("/register/")
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
    
   
@router.post("/login/")
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
    

@router.post("/forgot-password/")
async def forgot_password(
    user_mail: EmailRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.forgot_password(user_mail=user_mail)
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post("/verify-code/")
async def verify_code(
    data: CodeRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.verify_code(data=data)
    except UserNotFoundError:
        return HTTPException(status_code=404, detail="Пользователь не найден")
    except InvalidCodeError:
        raise HTTPException(status_code=400, detail="Неверный код")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


@router.post("/reset-password/")
async def reset_password(
    data: CodeUpdateRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return await auth_service.reset_password(data=data)
    except UserNotFoundError:
        return HTTPException(status_code=404, detail="Пользователь не найден")
    except InvalidCodeError:
        raise HTTPException(status_code=400, detail="Неверный код")
    except AppError as err:
        detail = str(err) or "Bad request"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail) from err


# @router.post("/send-mail/")
# async def send_mail(emails: EmailSchema):
#     list_emails = emails.emails

#     html = "<h1>Welcome to the app</h1>"

#     message = create_message(
#         recipients=list_emails,
#         subject="Welcome",
#         body=html
#     )
#     mail = get_mail()
#     await mail.send_message(message)

#     return {"message": "Email send succesfully"}
