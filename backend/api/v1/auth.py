from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from core.dependency import get_current_user,create_access_token,authenticate_user,get_user_email,hash_password,verify_access_token,create_refresh_token,save_refresh_token,verify_refresh_token,get_refresh_token,revoke_refresh_token,
from db.session import get_db
from sqlalchemy.orm import Session
from model.users.user_schema import UserResponse , UserCreate,RefreshRequest
from model.users.users import User
router = APIRouter(prefix="/v1/auth",tags=["authentication"])

@router.post("/login")
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = authenticate_user(form.username,form.password,db)
    access_token = create_access_token(data={"sub":str(user.id)})
    refresh_token = create_refresh_token(user.id)
    save_refresh_token(
        db,
        user.id,
        refresh_token
    )
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer"
    }
@router.get("/profile")
def get_profile(
    current_user = Depends(get_current_user)
):
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
@router.post("/register")
def register(user:UserCreate,db:Session=Depends(get_db)):
    existing = get_user_email(user.email)
    if existing:
        raise HTTPException(status_code=400,detail="email already exists")
    db_user = User(email=user.email,password_hash=hash_password(user.password))
    db.add(db_user)
    db.close()
    return {"message":"user is created"}
@router.post("/refresh")
def refresh(data:RefreshRequest,db:Session=Depends(get_db)):
    payload = verify_refresh_token(data.refreshtoken)
    if payload is None:
        raise HTTPException(status_code=401,detail="invalid refresh token")
    db_token = get_refresh_token(db,data.refreshtoken)
    if db_token is None:
        raise HTTPException(status_code=401,detail="token not found")
    if db_token.revoked:
        raise HTTPException(status_code=401,detail="token is revoked")
    revoke_refresh_token(db,data.refreshtoken)
    access_token = create_access_token(int(payload["sub"]))
    refresh_token = create_refresh_token(int,payload["sub"])
    save_refresh_token(db,payload["sub"],int(payload["sub"]),refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.post("/logout")
def logout(data:RefreshRequest,db:Session=Depends(get_db)):
    revoke_refresh_token(db,data.refreshtoken)
    return {
        "message":"logged out "
    }