# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.utils.security import verify_password, create_access_token, get_db
from app.config import settings
from sqlalchemy.orm import Session
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db_local():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username is the email in our flow
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
    finally:
        db.close()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
