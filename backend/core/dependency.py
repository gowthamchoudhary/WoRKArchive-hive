from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.config import settings
from jose import JWTError,jwt
from passlib.context import CryptContext
from datetime import timedelta,datetime
from model.users.users import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"] ,deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES

def  verify_token(token):
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    user_id = payload.get("sub")
  
    return user_id

def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db):
    user_id=verify_token(token)
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=401,detail="user not found")
    return db_user
def hash_password(password):
    return pwd_context.hash(password)
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)


def create_access_token(data:dict):
    to_encode = data.copy()
    exp = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':exp})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username:str,password:str,db):
    db_user = db.query(User).filter(User.email==username).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="user not found")
    if not verify_password(password,db_user.password_hash):
        raise HTTPException(status_code=401,detail="authentication failed")
    
    