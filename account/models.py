from app.database import Base
from datetime import datetime

from sqlalchemy import (Column, 
                        Boolean, 
                        String, 
                        Integer, 
                        DateTime,
                        ForeignKey
                    )

class Accounts(Base):
    __tablename__ = "Clients"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String, unique=True)
    email            = Column(String, unique=True)
    phone_number     = Column(String)
    hashed_password  = Column(String)
    is_active        = Column(Boolean, default=True)
    is_superuser     = Column(Boolean, default=False)


class Questions(Base):
    __tablename__ = "Clients-Requests"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String, ForeignKey("Clients.username"))
    question         = Column(String)
    created_at       = Column(DateTime, default=datetime.utcnow())
