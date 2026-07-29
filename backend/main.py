from fastapi import FastAPI,Request,HTTPException,Depends
from api.v1 import auth
from api.v1 import github
from core.dependency import get_current_user
app = FastAPI(title="todays goal",version="1.0.0")
app.include_router(auth.router)
app.include_router(github.router)

@app.get("/")
def get_me():
    return {"message": "God Loves you"}
@app.get("/dashboard")
def dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Welcome {current_user.username}!",
        "user": current_user
    }   

@app.get("/profile")
def get_profile(
    current_user = Depends(get_current_user)
):
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }