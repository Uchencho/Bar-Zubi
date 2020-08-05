from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import get_user_by_username


# openssl rand -hex 32
SECRET_KEY = "3525b9e881f4d0c5d530b334fca352e5cb4b2ba9ecd5b046b8afec1619780e41"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_schema = OAuth2PasswordBearer(tokenUrl='token')

def verify_password(plain_password, hashed_password):
    """
    Compares the passed in plain password and the hashed one stored in the db
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hashes a password using bcrypt
    """
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    db_user = get_user_by_username(db, username=username)
    if not db_user:
        # If User does not exist
        return False
    if not verify_password(password, db_user.hashed_password):
        # If the password is incorrect
        return False
    return db_user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Application/json" : "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user