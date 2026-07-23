from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from core.config import settings

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

