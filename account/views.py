from sqlalchemy.orm import Session
from .schema import RegisterSchema, EnquirySchema
from .serializer import get_password_hash
from .models import Accounts, Questions

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

def get_enquiry(db: Session, username: str):
    return db.query(Questions).filter(Questions.username == username).all()

def get_enquiry_by_id(db: Session, username: str, enquire_id: int):
    return db.query(Questions).filter(Questions.username == username, 
                                      Questions.id == enquire_id).all()

def update_enquiry(db: Session, username: str, enquire_id: int, question: str):
    question_mod = db.query(Questions).filter(Questions.username == username, 
                                      Questions.id == enquire_id).first()
    if question_mod == None:
        return None
    question_mod.question = question
    db.commit()
    db.refresh(question_mod)
    return question_mod

def create_enquiry(db: Session, inp_enq: EnquirySchema):
    enq_mod = Questions(username=inp_enq.username, question=inp_enq.question)
    db.add(enq_mod)
    db.commit()
    db.refresh(enq_mod)
    return enq_mod