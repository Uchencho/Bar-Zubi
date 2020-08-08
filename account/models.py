from app.database import Base

from sqlalchemy import Column, Boolean, String, Integer

class Accounts(Base):
    __tablename__ = "Clients"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String, unique=True)
    email            = Column(String, unique=True)
    phone_number     = Column(String)
    hashed_password  = Column(String)
    is_active        = Column(Boolean, default=True)
    is_superuser     = Column(Boolean, default=False)