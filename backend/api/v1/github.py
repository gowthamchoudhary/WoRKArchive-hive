from fastapi.responses import RedirectResponse
from fastapi import APIRouter,Depends
from core.config import settings
from db.session import get_db
from model.users.users import User
from model.connections.connection import Connection
from sqlalchemy.orm import session
from core.dependency import get_current_user
router = APIRouter(prefix="/api/v1/auth/github",tags=["Authentication"])



@router.get("/login")
def login_github():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=read:user user:email"
    )
    return RedirectResponse(github_auth_url)

@router.get("/callback")
async def github_callback(code:str,current_user:session=Depends(get_current_user)):
    access_token = exchange_code_for_access_token(code)
    github_user_info = get_github_user_info(access_token)
    


async def exchange_code_for_access_token(code:str):
    pass
async def get_github_user_info(access_token):
    pass