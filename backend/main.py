from fastapi import FastAPI, Depends, HTTPException, Security, status
from typing import  Annotated
from models import User
from database import get_db_session
from sqlalchemy.orm import Session 
import auth
from auth import get_current_user
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3006",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
]

app = FastAPI()
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_dependency = Annotated[Session, Depends(get_db_session)]
user_dependency = Annotated[User, Depends(get_current_user)]
@app.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user
