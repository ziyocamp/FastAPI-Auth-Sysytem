from random import randint

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi_mail import FastMail, MessageSchema

from .database import get_db

from .schemas import UserCreate
from .models import User

from passlib.context import CryptContext

from .config import mail_conf


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["Auth Endpoints"]
)

@router.post("/register")
async def register_api(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    verification_code = randint(100000, 999999)
    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        hashed_password = hashed_password,
        is_active = False,
        is_verified = False,
        verification_code = verification_code
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    message = MessageSchema(
        subject="Verification Code",
        recipients=[user.email],
        body=f"Tasdiqlash kod: {verification_code}",
        subtype="plain"
    )

    fm = FastMail(mail_conf)
    await fm.send_message(message)

    return {"message": "Email sent in the background"}

