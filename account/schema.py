from typing import List, Optional
from pydantic import BaseModel

class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    phone_number: Optional[str] = "None"

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class LoginCredentials(BaseModel):
    username: str
    password: str

class EnquirySchema(BaseModel):
    question: str
    username: Optional[str] = "None"

class AllEnquirySchema(BaseModel):
    id: int
    username: str
    question: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None