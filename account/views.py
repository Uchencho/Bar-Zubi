from sqlalchemy.orm import Session
from .schema import RegisterSchema
from .serializer import get_password_hash
from .models import Accounts

def register_user(db: Session, user: RegisterSchema):
    pw = get_password_hash(user.password)
    db_user = Accounts(email=user.email, username=user.username, 
                        hashed_password=pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user