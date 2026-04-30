from typing import List

from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
   email: EmailStr

class EmailSchema(BaseModel):
   emails: List[EmailStr]

class CodeRequest(BaseModel):
   email: str
   code: str

class CodeUpdateRequest(BaseModel):
   code: str
   email: EmailStr
   new_password: str