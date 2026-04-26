from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Seat
LOCK_TIMEOUT = timedelta(minutes=1)

def lock_seat(db: Session, seat_id: int, user_id: int):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).with_for_update().first()
        if not seat:
            raise HTTPException(404, "Seat not found")

        release_expired_lock(seat)

        if seat.status == "booked":
            raise HTTPException(409, "Already booked")

        if (
            seat.status == "locked"
            and seat.locked_at
            and datetime.utcnow() - seat.locked_at < LOCK_TIMEOUT
            and seat.locked_by != user_id
        ):
            raise HTTPException(400, "Seat temporarily locked")

        seat.status = "locked"
        seat.locked_at = datetime.utcnow()
        seat.locked_by = user_id

        db.commit()
        return seat

    except Exception:
        db.rollback()
        raise

def book_seat(db: Session, seat_id: int, user_id: int):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).with_for_update().first()
        if not seat:
            raise HTTPException(404, "Seat not found")

        release_expired_lock(seat)

        if seat.status != "locked":
            raise HTTPException(400, "Seat not locked")

        if seat.locked_by != user_id:
            raise HTTPException(403, "Not your seat")

        seat.status = "booked"
        seat.locked_at = None
        seat.locked_by = None

        db.commit()
        return seat

    except Exception:
        db.rollback()
        raise

def release_expired_lock(seat: Seat):
    if (
        seat.status == "locked"
        and seat.locked_at
        and datetime.utcnow() - seat.locked_at > LOCK_TIMEOUT
    ):
        seat.status = "available"
        seat.locked_at = None
        seat.locked_by = None