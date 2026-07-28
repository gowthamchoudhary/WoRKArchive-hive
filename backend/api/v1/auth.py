from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from core.dependency import get_current_user,verify_password,create_access_token
from db.session import get_db
from sqlalchemy.orm import Session
router = APIRouter(prefix="/v1/auth",tags=["authentication"])

@router.get("/login")
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = get_current_user(form.username)
    if not user:
        raise HTTPException(status_code=401,detail="no user is found")
    if not verify_password(plain_password=form.password,hashed_password=user.password_hash):
        raise HTTPException(status_code=401,detail="invalid password")
    token = create_access_token(data={"sub":str(user.id)})
    return {
        "access_token":token,
        "token_type":"bearer"
    }
@router.get("/profile")
def get_profile(
    current_user = Depends(get_current_user)
):
    return current_user