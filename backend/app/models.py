from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base

# --- User model ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # store hashed passwords only

# --- Seat model ---
class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True)
    status = Column(String, default="available", nullable=False)  # available, locked, booked
    locked_at = Column(DateTime, nullable=True)                   # timestamp when locked
    locked_by = Column(Integer, nullable=True)                    # user ID who locked it
