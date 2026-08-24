from fastapi import FastAPI,APIRouter,Depends,HTTPException,Query

from model.summary.summary import WorkSummary
from sqlalchemy.orm import Session
from time import time
from services.llm_service import analyze_work
from services.post_service import generate_post
from model.summary.summary import WorkSummary
from db.session import get_db
from core.dependency import get_current_user, create_access_token
router = APIRouter(prefix="/post")

@router.get("/generate_post")
async def generate_post(
     post_time: time,
        timezone: str = Query("Asia/Kolkata"),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):  
        db_llm_summary = db.query(WorkSummary).filter(WorkSummary.user_id==current_user.id).