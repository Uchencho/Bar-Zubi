from sqlalchemy.orm import Session
from .schema import RegisterSchema
from .serializer import get_password_hash
from .models import Accounts

def register_user(db: Session, user: RegisterSchema):
    pw = get_password_hash(user.password)
    db_user = Accounts(email=user.email, username=user.username, 
                        hashed_password=pw, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int=0, limit: int=10):
    return db.query(Accounts).offset(skip).limit(limit).all()

def get_user_by_username(db: Session, username: str):
    return db.query(Accounts).filter(Accounts.username == username).first()