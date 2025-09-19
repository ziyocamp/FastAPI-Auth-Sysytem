from fastapi import FastAPI

from .database import Base, engine
from .models import User, Task

app = FastAPI(title="Auth System")

Base.metadata.create_all(engine)

@app.get("/")
async def home():
    return {"message": "Auth System"}

