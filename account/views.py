from sqlalchemy.orm import Session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
from .schema import RegisterSchema, EnquirySchema
from .serializer import get_password_hash
from .models import Accounts, Questions
import settings

def register_user(db: Session, user: RegisterSchema):
    pw = get_password_hash(user.password)
    db_user = Accounts(email=user.email, username=user.username, 
                        hashed_password=pw, phone_number=user.phone_number,
                        is_superuser=user.is_superuser)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int=0, limit: int=20):
    return db.query(Accounts).offset(skip).limit(limit).all()

def get_user(db: Session, username: str, email: str):
    return db.query(Accounts).filter(Accounts.username == username, 
                                    Accounts.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(Accounts).filter(Accounts.username == username).first()

def get_enquiry(db: Session, username: str):
    return db.query(Questions).filter(Questions.username == username).all()

def all_enquiries(db: Session):
    return db.query(Questions).all()

def get_enquiry_by_id(db: Session, username: str, enquire_id: int):
    return db.query(Questions).filter(Questions.username == username, 
                                      Questions.id == enquire_id).all()

def update_profile(db: Session, username: str, phone_number: str):
    user_profile = db.query(Accounts).filter(Accounts.username==username).first()
    user_profile.phone_number = phone_number
    db.commit()
    db.refresh(user_profile)
    return user_profile

def update_enquiry(db: Session, username: str, enquire_id: int, question: str):
    question_mod = db.query(Questions).filter(Questions.username == username, 
                                      Questions.id == enquire_id).first()
    if question_mod == None:
        return None
    question_mod.question = question
    db.commit()
    db.refresh(question_mod)
    return question_mod

def delete_enquiry(db: Session, username: str, enquire_id: int, question: str):
    question_mod = db.query(Questions).filter(Questions.username == username, 
                                      Questions.id == enquire_id)
    if question_mod.first() == None:
        return None
    question_mod.delete()
    db.commit()
    return "Deleted Successfully"

def create_enquiry(db: Session, inp_enq: EnquirySchema):
    enq_mod = Questions(username=inp_enq.username, question=inp_enq.question)
    db.add(enq_mod)
    db.commit()
    db.refresh(enq_mod)
    return enq_mod

def send_email(recepient: str, username: str):
    from_address = settings.EMAIL_HOST_USER
    pw = settings.EMAIL_HOST_PASSWORD
    reply_to = settings.EMAIL_HOST_USER

    msg = MIMEMultipart()
    msg['From'] = "Barister Zubi"
    msg["To"] = recepient
    msg["In-Reply-To"] = reply_to
    msg["Subject"] = "Barrister Zubi Enterprise"
    body = f"Welcome distinguished {username}, rest assured you have been placed in safe hands"
    msg.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", settings.EMAIL_PORT, context=context) as server:
        try:
            server.login(from_address, pw)
        except smtplib.SMTPAuthenticationError:
            pass
        text = msg.as_string()
        server.sendmail(from_address, recepient, text)