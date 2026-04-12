from app.auth import hash_password, verify_password, create_access_token
from app.models import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def create_user(db: Session, username: str, password: str):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(400, "Username already exists")

    if len(password) < 8:
        raise HTTPException(400, "Password too short")

    user = User(
        username=username,
        hashed_password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return token


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return create_access_token({"sub": str(user.id)})