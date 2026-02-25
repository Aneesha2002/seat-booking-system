from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import random
from fastapi.security import OAuth2PasswordRequestForm
from app.db import SessionLocal, engine
from app.models import Seat, Base, User
from app.schemas import SeatOut, UserCreate, Token
from app.auth import create_access_token, get_current_user
from app.auth import verify_password,hash_password
# --- App setup ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOCK_TIMEOUT = timedelta(minutes=1)

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Startup ---
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Seat).count() == 0:
        for i in range(1, 31):
            db.add(Seat(id=i))
        db.commit()
    db.close()


# =========================
# Auth Routes
# =========================

@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if len(user.password) < 6:
        raise HTTPException(status_code=400,detail="Password must be at least 6 characters")



    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

# =========================
# Health
# =========================

@app.get("/")
def health():
    return {"status": "ok"}

# =========================
# Seat Routes (JWT Protected)
# =========================

@app.post("/seats/init")
def init_seats(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    if db.query(Seat).count() > 0:
        return {"message": "Seats already initialized"}

    for i in range(1, 31):
        db.add(Seat(id=i, status="available"))

    db.commit()
    return {"message": "30 seats created"}


@app.get("/seats", response_model=List[SeatOut])
def list_seats(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    cleanup_expired_locks(db)
    return db.query(Seat).all()


@app.post("/seats/{seat_id}/lock")
def lock_seat(
    seat_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    seat = (
        db.query(Seat)
        .filter(Seat.id == seat_id)
        .with_for_update()
        .first()
    )

    if not seat:
        raise HTTPException(404, "Seat not found")

    if seat.status == "booked":
        raise HTTPException(400, "Seat already booked")

    if (
        seat.status == "locked"
        and seat.locked_at
        and datetime.utcnow() - seat.locked_at < LOCK_TIMEOUT
        and seat.locked_by != current_user
    ):
        raise HTTPException(400, "Seat temporarily locked")

    seat.status = "locked"
    seat.locked_at = datetime.utcnow()
    seat.locked_by = current_user

    db.commit()
    return {"message": "Seat locked"}


@app.post("/seats/{seat_id}/book")
def book_seat(
    seat_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    seat = (
        db.query(Seat)
        .filter(Seat.id == seat_id)
        .with_for_update()
        .first()
    )

    if not seat:
        raise HTTPException(404, "Seat not found")

    if seat.status != "locked":
        raise HTTPException(400, "Seat not locked")

    if seat.locked_by != current_user:
        raise HTTPException(403, "Not your seat")

    if datetime.utcnow() - seat.locked_at > LOCK_TIMEOUT:
        raise HTTPException(400, "Lock expired")

    # --- Payment simulation ---
    if not random.choice([True, True, True, False]):
        raise HTTPException(402, "Payment failed")

    seat.status = "booked"
    seat.locked_at = None

    db.commit()
    return {"message": "Seat booked successfully"}


@app.post("/seats/reset")
def reset_seats(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    db.query(Seat).delete()
    db.commit()
    return {"message": "All seats deleted"}

# =========================
# Helpers
# =========================

def cleanup_expired_locks(db: Session):
    expired = db.query(Seat).filter(
        Seat.status == "locked",
        Seat.locked_at < datetime.utcnow() - LOCK_TIMEOUT
    ).all()

    for seat in expired:
        seat.status = "available"
        seat.locked_at = None
        seat.locked_by = None

    db.commit()
