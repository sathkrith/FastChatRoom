from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import  get_db_session
from fastapi import status

from models import User
# Configuration
SECRET_KEY = "121432413423k1h23jk41g2kj3h4gk21juyf4gl312134khg21lk3h4ljk21h3g4kujy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
   tags=["authentication"],
   prefix="/auth"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


db_dependency = Annotated[Session, Depends(get_db_session)]

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, request: CreateUserRequest):
    create_user = User(
        username=request.username,
        email=request.email, 
        password=pwd_context.hash(request.password))
    db.add(create_user)
    await db.commit()
    response = JSONResponse()
    response.body = "User created successfully"


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = await authenticated_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(user.username, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response = JSONResponse(content="Logged in successfully", status_code=status.HTTP_200_OK)
    response.set_cookie(key = "access_token", value=f"Bearer {access_token}",  max_age=1800, expires=1800, secure=True, httponly=True, samesite="none")
    return response

async def authenticated_user(username: str, password: str, db: Session):
    statemenent = select(User).where(User.username == username)
    user =await db.execute(statemenent)  
    #user = db.query(User).filter(User.username == username).first()
    user = user.scalars().one_or_none()
    if user is None:
        print("User not found")
        return False
    if not pwd_context.verify(password, user.password):
        print("Password incorrect")
        return False
    return user

def create_access_token(username:str, user_id:int, expires_delta: timedelta):
    to_encode = {"sub": username, "user_id": user_id}
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str,Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"username": username, "user_id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate JWT" + str(e))
