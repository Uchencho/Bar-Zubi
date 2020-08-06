from typing import List, Optional
from pydantic import BaseModel

class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    

    class Config:
        orm_mode = True


class LoginCredentials(BaseModel):
    username: str
    password: str