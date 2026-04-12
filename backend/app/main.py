from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal, engine
from app.models import Base
from app.schemas import UserCreate, Token, SeatOut

from app.auth import get_current_user
from app.services.auth_service import create_user, authenticate_user
from app.services.seat_service import (
    lock_seat,
    book_seat,
    cleanup_expired_locks
)

# -------------------------
# App setup
# -------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://seat-booking-system-omega.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Startup
# -------------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# -------------------------
# Health check
# -------------------------
@app.get("/")
def health():
    return {"status": "ok"}

# -------------------------
# Auth Routes
# -------------------------
@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    token = create_user(db, user.username, user.password)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    token = authenticate_user(db, user.username, user.password)
    return {"access_token": token, "token_type": "bearer"}

# -------------------------
# Seat Routes (Protected)
# -------------------------
@app.get("/seats", response_model=List[SeatOut])
def list_seats(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    cleanup_expired_locks(db)
    return db.query(Seat).order_by(Seat.id).all()


@app.post("/seats/{seat_id}/lock")
def lock(
    seat_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    seat = lock_seat(db, seat_id, current_user)
    return {
        "status": seat.status,
        "seat_id": seat.id
    }


@app.post("/seats/{seat_id}/book")
def book(
    seat_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    seat = book_seat(db, seat_id, current_user)
    return {
        "message": "Seat booked successfully",
        "seat_id": seat.id
    }