from fastapi import FastAPI,Request,HTTPException,Depends
from api.v1 import auth
from api.v1 import github
app = FastAPI(title="todays goal",version="1.0.0")
app.include_router(auth.router)
app.include_router(github.router)

@app.get("/")
def get_me():
    return {"message": "God Loves you"}