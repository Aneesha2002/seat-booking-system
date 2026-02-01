from sqlalchemy import Column,Integer,String, DateTime
from app.db import Base

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer,primary_key=True,index=True)
    status = Column(String,default="AVAILABLE") # AVAILABLE | LOCKED | BOOKED 
    locked_at= Column(DateTime,nullable=True)
    locked_by = Column(Integer,nullable=True)
