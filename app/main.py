from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy.orm import Session

from account import models
from .database import SessionLocal, engine
from account.schema import (
                            RegisterSchema, UserSchema, 
                            LoginCredentials, EnquirySchema,
                            AllEnquirySchema)

from account.views import (
                            register_user, get_user_by_username, 
                            get_users, create_enquiry,
                            get_enquiry, get_enquiry_by_id,
                            update_enquiry, delete_enquiry
                            )

from account.serializer import (
                                authenticate_user, 
                                create_access_token, 
                                check_auth, 
                                create_refresh_token
                                )

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.get("/healthcheck")
async def healthcheck():
    return {"Message" : "Bar Zubi is working efficiently"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=UserSchema)
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username is already registered")
    return register_user(db=db, user=user)

@app.post("/login")
def login(response: Response, cred: LoginCredentials, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, username=cred.username, password=cred.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})
    response.set_cookie(key="refresh", value=refresh_token, httponly=True)

    return {
        "username" : db_user.username,
        "email" : db_user.email,
        "phone_number" : db_user.phone_number,
        "is_active" : db_user.is_active,
        "access_token" : access_token
    }

@app.get("/users", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int=100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users
    
@app.get("/auth_users")
def read_auth_users(response: Response, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    authorized, username = check_auth(token)
    if authorized:
        db_user = get_user_by_username(db, username=username)
        return db_user
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message" : "Authentication credentials were not provided"}


@app.post("/enquiry")
def make_enquiry(enq: EnquirySchema, response: Response, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    authorized, username = check_auth(token)
    if authorized:
        enq.username = username
        return create_enquiry(db=db, inp_enq=enq)
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message" : "Authentication credentials were not provided"}


@app.get("/enquiries")
def all_questions(response: Response, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    authorized, username = check_auth(token)
    if authorized:
        questions = get_enquiry(db, username=username)
        return questions
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message" : "Authentication credentials were not provided"}


@app.get("/enquiries/{enquire_id}")
def question_detail(response: Response, enquire_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    authorized, username = check_auth(token)
    if authorized:
        question = get_enquiry_by_id(db, username=username, enquire_id=enquire_id)
        if len(question) > 0:
            return question
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message" : "Not Found"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message" : "Authentication credentials were not provided"}


@app.put("/enquiries/{enquire_id}")
def edit_question(enq: EnquirySchema, response: Response, enquire_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    authorized, username = check_auth(token)
    if authorized:
        question = update_enquiry(db, username=username, enquire_id=enquire_id, question=enq.question)
        if question == None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message" : "Not Found"}
        return question
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message" : "Authentication credentials were not provided"}


@app.delete("/enquiries/{enquire_id}")
def del_question(enq: EnquirySchema, response: Response, enquire_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    authorized, username = check_auth(token)
    if authorized:
        question = delete_enquiry(db, username=username, enquire_id=enquire_id, question=enq.question)
        if question == None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message" : "Not Found"}
        response.status_code = status.HTTP_204_NO_CONTENT
        return question
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message" : "Authentication credentials were not provided"}
