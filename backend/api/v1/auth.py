from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.dependency import get_current_user,create_access_token,authenticate_user
from db.session import get_db
from sqlalchemy.orm import Session
router = APIRouter(prefix="/v1/auth",tags=["authentication"])

@router.post("/login")
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = authenticate_user(form.username,form.password,db)
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
