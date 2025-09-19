from fastapi import FastAPI

from .database import Base, engine
from .models import User, Task

from .routers import router

app = FastAPI(title="Auth System")

Base.metadata.create_all(engine)

app.include_router(router)


@app.get("/")
async def home():
    return {"message": "Auth System"}

