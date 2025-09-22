from random import randint
from datetime import datetime, timedelta

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from fastapi_mail import FastMail, MessageSchema

from .database import get_db

from .schemas import UserCreate, UserVerify, UserLogin
from .models import User, Task

from passlib.context import CryptContext

from .config import mail_conf, settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["Auth Endpoints"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def register_api(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    verification_code = randint(100000, 999999)
    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        role='user',
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


@router.post("/verify")
async def verify_api(user_verify: UserVerify, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == user_verify.email).first()

    if user:
        if user.verification_code == user_verify.verification_code:
            user.is_active = True
            user.is_verified = True

            db.add(user)
            db.commit()

            return {"message": "success"}

        else:
            raise HTTPException(status_code=400, detail="siz xato verification code yubordingiz")
    else:
        raise HTTPException(status_code=400, detail="bunday user topilmadi")


@router.post("/login")
async def login_api(user_data: UserLogin, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == user_data.email, User.is_verified == True, User.is_active == True).first()

    if user:
        is_valid = pwd_context.verify(user_data.password, user.hashed_password)

        if is_valid:
            payload = {
                'sub': str(user.user_id),
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(minutes=15)
            }
            token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
            return {"token": token}
        else:
            raise HTTPException(status_code=401, detail="password xato")
    else:
        raise HTTPException(status_code=400, detail="bunday user topilmadi")

@router.post("/tasks")
async def task_api(task_data: dict, db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]):
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    user_id = int(payload['sub'])

    user = db.query(User).filter(User.user_id == user_id).first()

    task = Task(
        title=task_data['title'],
        descriptioin=task_data['descriptioin'],
        user_id=user.user_id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task
