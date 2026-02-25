from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    username: str
    password: str  # raw password for signup/login; will be hashed in backend

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Seat Schemas ---
class SeatOut(BaseModel):
    id: int
    status: str
    locked_by: Optional[int] = None  # user ID or None if unlocked
    locked_at: datetime | None

    class Config:
        from_attributes = True

