from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.config import settings
from jose import JWTError,jwt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from model.users.users import User

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES

def decode_token(token):
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    user_id = payload.get("sub")
  
    return user_id

def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:Session=Depends(get_db)):
    user_id=decode_token(token)
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=401,detail="user not found")
    return db_user
    