from fastapi import APIRouter, Depends,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from db.session import get_db
from core.dependency import get_current_user, create_access_token
from model.connections.connection import Connection
import httpx
from services.github_service import (
    get_github_login_url,
    exchange_code_for_access_token,
    get_github_user_info,
    get_github_user_email,
    get_user_events
)
router = APIRouter(
    prefix="/api/v1/auth/github",
    tags=["Authentication"],
)
@router.get("/login")
async def login_github():
    github_url = await get_github_login_url()
    return RedirectResponse(github_url)


@router.get("/callback")
async def github_callback(
    code: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    access_token = await exchange_code_for_access_token(code)
    provider = "github"
    github_user = await get_github_user_info(access_token)
    github_user_emails = await get_github_user_email(access_token)
    github_provider_user_id = str(github_user["id"])
    db_connection = db.query(Connection).filter(Connection.provider_user_id==github_provider_user_id, Connection.provider == "github").first()

    email = None
    for item in github_user_emails:
        if item.get("primary") and item.get("verified"):
           email = item["email"]
        break
    if db_connection:
        db_connection.provider_user_id = github_provider_user_id
        db_connection.username = github_user["login"]
        db_connection.avatar_url = github_user["avatar_url"]
        db_connection.profile_url = github_user["html_url"]
        db_connection.access_token = access_token
        db_connection.email = email
    else:
        db_connection = Connection(
                user_id=current_user.id,
                provider=provider.lower(),
                provider_user_id=github_provider_user_id,
                username=github_user["login"],
                avatar_url=github_user["avatar_url"],
                profile_url=github_user["html_url"],
                access_token=access_token,
                email=email,
            )
        db.add(db_connection)  
    db.commit()
    db.refresh(db_connection)

    jwt_token =  create_access_token(
       {
           "sub":str(current_user.id),
       }
    )
    response = RedirectResponse(url="/dashboard")

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response
@router.post("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie(key="access_token")
    return response
@router.get("/me")
def get_github_me(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    user_id = current_user.id
    db_github = db.query(Connection).filter(Connection.user_id==user_id,Connection.provider=="github").first()
    if not db_github:
        raise HTTPException(status_code=401,detail="users github info is not found  ")
    
    return{
        "username":db_github.username,
        "email":db_github.email,
        "avatar_url":db_github.avatar_url,
        "profile_url":db_github.profile_url,
        "provider":db_github.provider
    }
@router.get("/activity")
async def get_github_activity(current_user=Depends(get_current_user),db:Session = Depends(get_db)):
    db_github = db.query(Connection).filter(Connection.user_id==current_user.id,Connection.provider=="github").first()
    if not db_github:
        raise HTTPException(status_code=401,detail="no github info is found")
    access_token = db_github.access_token
    events = await get_user_events(db_github.username,access_token)

    return {
        "provider":"github",
        "events":events
    }
