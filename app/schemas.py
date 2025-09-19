from typing import Annotated
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    first_name: Annotated[str, Field(min_length=3, max_length=64)]
    last_name:  Annotated[str | None, Field(min_length=3, max_length=64)] = None
    email:      Annotated[str, EmailStr()]
    password:   Annotated[str, Field(min_length=8)]


class UserVerify(BaseModel):
    email: Annotated[str, EmailStr()]
    verification_code: int


class UserLogin(BaseModel):
    email: Annotated[str, EmailStr()]
    password: Annotated[str, Field(min_length=8)]
