from fastapi.responses import RedirectResponse
from fastapi import APIRouter


router = APIRouter(prefix="/api/v1/auth/github",tags=["Authentication"])



@router.get("/login")
def login_github():
    return RedirectResponse("https://google.com")