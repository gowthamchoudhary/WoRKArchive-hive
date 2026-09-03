from fastapi import FastAPI,Request,HTTPException,Depends
from api.v1 import auth
from db.session import Base,engine
from api.v1 import github
from routes import posts
from fastapi.middleware.cors import CORSMiddleware
from core.dependency import get_current_user
app = FastAPI(title="todays goal",version="1.0.0")
app.include_router(auth.router)
app.include_router(github.router)
app.include_router(posts.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def get_me():
    return {"message": "God Loves you"}
  

@app.get("/profile")
def get_profile(
    current_user = Depends(get_current_user)
):
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
@app.get("/dashboard")
def dashboard(current_user = Depends(get_current_user)):
    return {
        "message": f"Welcome {current_user.username}!",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        },
    }