from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import views
from .schema import TokenData

# openssl rand -hex 32
SECRET_KEY = "3525b9e881f4d0c5d530b334fca352e5cb4b2ba9ecd5b046b8afec1619780e41"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    db_user = views.get_user_by_username(db, username=username)
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
        expire = datetime.utcnow() + timedelta(minutes=240)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp" : expire})
    refresh_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_jwt

def check_auth(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            return False, "None"
        token_data = TokenData(username=username)
    except JWTError:
        return False, "None"
    return True, token_data.username


def check_basic_auth(token: str):
    if token == "99b09388ebc52a5264c8e1c8c16dabee37e08834e901a27e2ecd4f8a29223334":
        return True
    return False

def check_admin_auth(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            return False, "None"
        token_data = TokenData(username=username)
        db_user = views.get_user_by_username(db, token_data.username)
        if db_user.is_superuser == False:
            return False, "None"
    except JWTError:
        return False, "None"
    return True, token_data.username

