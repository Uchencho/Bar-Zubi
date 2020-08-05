from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import crud, models, schema
from account.schema import RegisterSchema, UserSchema
from account.views import register_user, get_users

models.Base.metadata.create_all(bind=engine)

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


@app.get("/users/{user_id}", response_model=schema.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/items", response_model=schema.Item)
def create_item_for_user(user_id: int, item: schema.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items", response_model=List[schema.Item])
def read_items(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.post("/register", response_model=UserSchema)
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username is already registered")
    return register_user(db=db, user=user)

@app.get("/users", response_model=List[UserSchema])
def all_users(skip: int=0, limit: int=10, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users
