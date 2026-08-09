from fastapi import APIRouter,Depends,HTTPException,Cookie
from fastapi.security import OAuth2PasswordRequestForm
from core.dependency import get_current_user,create_access_token,authenticate_user,get_user_email,hash_password,verify_access_token,create_refresh_token,save_refresh_token,verify_refresh_token,get_refresh_token,revoke_refresh_token
from db.session import get_db
from sqlalchemy.orm import Session
from model.users.user_schema import UserResponse , UserCreate,RefreshRequest
from fastapi.responses import JSONResponse
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
    response = JSONResponse(
        content={
            "message":"Logged in successfully",
            "token_type":"Bearer"
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60

    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7

    )
    return response

@router.post("/register")
def register(user:UserCreate,db:Session=Depends(get_db)):
    existing = get_user_email(user.email,db)
    if existing:
        raise HTTPException(status_code=400,detail="email already exists")
    db_user = User(email=user.email,password_hash=hash_password(user.password),username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message":"user is created"}
@router.post("/refresh")
def refresh(refresh_token:str | None = Cookie(default=None),db:Session=Depends(get_db)):
    if refresh_token is None:
        raise HTTPException(status_code=401,detail="refresh token is missing")
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401,detail="invalid refresh token")
    db_token = get_refresh_token(db,refresh_token)
    if db_token is None:
        raise HTTPException(status_code=401,detail="token not found")
    if db_token.revoked:
        raise HTTPException(status_code=401,detail="token is revoked")
    revoke_refresh_token(db,refresh_token)
    user_id = int(payload["sub"])
    new_access_token = create_access_token({"sub":str(user_id)})
    new_refresh_token = create_refresh_token(user_id)
    save_refresh_token(db=db,user_id=user_id,token=new_refresh_token)
    response = JSONResponse(
        content={
            "message":"token refreshed",
            "token_type":"Bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7
    )
    return response
@router.post("/logout")
def logout(
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if refresh_token:
        revoke_refresh_token(db, refresh_token)

    response = JSONResponse(content={"message": "logged out"})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response
