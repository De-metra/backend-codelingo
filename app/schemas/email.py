from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, conint, model_validator
from typing import Optional, Any
import re
from typing import List


class EmailRequest(BaseModel):
   email: EmailStr

class EmailSchema(BaseModel):
   emails: List[EmailStr]

class CodeRequest(BaseModel):
   email: str
   code: str

class CodeUpdateRequest(BaseModel):
   email: EmailStr
   new_password: str