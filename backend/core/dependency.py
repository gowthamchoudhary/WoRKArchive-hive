from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends,HTTPException,Cookie
from sqlalchemy.orm import Session
from db.session import get_db
from core.config import settings
from jose import JWTError,jwt
from passlib.context import CryptContext
from datetime import timedelta,datetime,timezone
from model.users.users import User,RefreshToken
import hashlib
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
pwd_context = CryptContext(schemes=["argon2"] ,deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS



def verify_token(token):
    try:
        return jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except JWTError:
        return None


def  verify_access_token(token):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401,detail="invalid token")
    user_id = payload.get("sub")    
    if user_id is None:
        raise HTTPException(status_code=401,detail="invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401,detail="invalid token")
    return user_id

def get_current_user(access_token:str | None = Cookie(default=None),db:Session=Depends(get_db)):
    if access_token is None:
        raise HTTPException(status_code=401,detail="not authenticated")
    user_id=verify_access_token(access_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="invalid token")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401,detail="invalid token")
    db_user = db.query(User).filter(User.id == user_id).first()
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
    to_encode.update({'exp':exp,"type":"access"})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username:str,password:str,db):
    db_user = db.query(User).filter(User.email==username).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="user not found")
    if not verify_password(password,db_user.password_hash):
        raise HTTPException(status_code=401,detail="authentication failed")
    
    return db_user
def get_user_email(email,db:Session=Depends(get_db)):
    return db.query(User).filter(User.email == email).first()
def create_refresh_token(user_id:int):
    expires = datetime.now(timezone.utc)+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub":str(user_id),
        "type":"refresh",
        "exp":expires,
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
def verify_refresh_token(token):
    payload = verify_token(token)
    if payload is None:
        return None
    if payload.get("type")!="refresh":
        return None
    return payload
def hash_refresh_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def save_refresh_token(db,user_id,token):
    expire = datetime.now(timezone.utc)+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(token),
        expire_at=expire,
        revoked=False,
    )
    db.add(db_token)
    db.commit()


def get_refresh_token(db,token):
    return db.query(RefreshToken).filter(RefreshToken.token_hash==hash_refresh_token(token)).first()
def revoke_refresh_token(db,token):
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash==hash_refresh_token(token)).first()
    if db_token:
        db_token.revoked = True
        db.commit()


# def get_current_user_from_cookie(
#         access_token:str = Cookie(None)
# )
    