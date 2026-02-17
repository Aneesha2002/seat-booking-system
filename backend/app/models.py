from sqlalchemy import Column,Integer,String, DateTime
from app.db import Base

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True)
    status = Column(String, default="available", nullable=False)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(Integer, nullable=True)

