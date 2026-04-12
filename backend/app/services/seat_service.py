from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Seat

LOCK_TIMEOUT = timedelta(minutes=1)


def lock_seat(db: Session, seat_id: int, user_id: int):
    seat = db.query(Seat).filter(Seat.id == seat_id).with_for_update().first()

    if not seat:
        raise HTTPException(404, "Seat not found")

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


def book_seat(db: Session, seat_id: int, user_id: int):
    seat = db.query(Seat).filter(Seat.id == seat_id).with_for_update().first()

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
    return seat


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