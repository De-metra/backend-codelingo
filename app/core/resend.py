import resend

from app.core.config import settings


resend.api_key = settings.RESEND_API_KEY


async def send_reset_mail(user_email: str, code: str):
    resend.Emails.send({
        "from": "Codelingo <onboarding@resend.dev>",
        "to": [user_email],
        "subject": "Codelingo | Восстановление пароля",
        "html": f"""
                Приветствуем!<br>
                
                Чтобы восстановить доступ к своему аккаунту, введите, пожалуйста, код:<br>

                <h1>{code}</h1>

                Если вы получили это письмо по ошибке, просто проигнорируйте его.
            """
    })