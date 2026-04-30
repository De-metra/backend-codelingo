from pydantic import BaseModel


class TokenReturn(BaseModel):
    access_token: str
    token_type: str = "bearer"

