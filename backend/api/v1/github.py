from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from db.session import get_db
from core.dependency import get_current_user, create_access_token
from model.connections.connection import Connection

from services.github_service import (
    get_github_login_url,
    exchange_code_for_access_token,
    get_github_user_info,
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

    github_user = await get_github_user_info(access_token)
    db_connection = db.query(Connection).filter(Connection.provider_user_id==github_user["id"], Connection.provider == "github").first()
    if db_connection:
        db_connection.provider_user_id=github_user["id"]
        username=github_user["login"],
        avatar_url=github_user["avatar_url"],
        profile_url=github_user["html_url"],
        access_token=access_token,
    else:
        db_connection = Connection(
                user_id=current_user.id,
                provider="github",
                provider_user_id=github_user["id"],
                username=github_user["login"],
                avatar_url=github_user["avatar_url"],
                profile_url=github_user["html_url"],
                access_token=access_token,
            )
        db.add(db_connection)

  
    db.commit()
    db.refresh(db_connection)

    jwt_token =  create_access_token(
       {
           "sub":db_connection.id,
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