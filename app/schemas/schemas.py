from pydantic import BaseModel


class MessageReturn(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
