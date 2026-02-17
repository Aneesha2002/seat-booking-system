from fastapi import FastAPI, Depends, HTTPException, Body 
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db import SessionLocal,engine
from app.models import Seat,Base
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.schemas import SeatOut

#App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


 #Create tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


#Dependency injection(DI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Config
LOCK_TIMEOUT = timedelta(minutes=1)

#Routes
@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/seats/init")
def init_seats(db: Session = Depends(get_db)):
    if db.query(Seat).count() > 0:
        return {"message": "Seats already initialized"}

    for i in range(1, 31):
        db.add(Seat(id=i))

    db.commit()
    return {"message": "30 seats created"}

@app.get("/seats", response_model=List[SeatOut])
def list_seats(db: Session = Depends(get_db)):
    cleanup_expired_locks(db)
    return db.query(Seat).all()


@app.post("/seats/{seat_id}/lock")
def lock_seat(
    seat_id: int,
    user_id: int = Body(...,embed=True),
    db: Session = Depends(get_db)
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
        if seat.locked_by != user_id:
            raise HTTPException(400, "Seat already booked")
    
    if (
    seat.status == "locked"
    and seat.locked_at
    and datetime.utcnow() - seat.locked_at < LOCK_TIMEOUT
    and seat.locked_by != user_id   # only block others
    ):
        raise HTTPException(400, "Seat temporarily locked")


    seat.status = "locked"
    seat.locked_at = datetime.utcnow()
    seat.locked_by = user_id

    db.commit()
    return {"message": "Seat locked"}

@app.post("/seats/{seat_id}/book")
def book_seat(
    seat_id: int,
    user_id: int = Body(..., embed=True),
    db: Session = Depends(get_db)
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

    if seat.locked_by != user_id:
        raise HTTPException(403, "Not your seat")

    if datetime.utcnow() - seat.locked_at > LOCK_TIMEOUT:
        raise HTTPException(400, "Lock expired")

    seat.status = "booked"
    seat.locked_at = None
    seat.locked_by = None

    db.commit()
    return {"message": "Payment successful"}

@app.post("/seats/reset")
def reset_seats(db: Session = Depends(get_db)):
    db.query(Seat).delete()
    db.commit()
    return {"message": "All seats deleted"}

def cleanup_expired_locks(db: Session):
    expired_seats = (
        db.query(Seat)
        .filter(
            Seat.status == "locked",
            Seat.locked_at < datetime.utcnow() - LOCK_TIMEOUT
        )
        .all()
    )

    for seat in expired_seats:
        seat.status = "available"
        seat.locked_at = None
        seat.locked_by = None

    db.commit()






