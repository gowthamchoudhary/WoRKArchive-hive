from fastapi import FastAPI,APIRouter,Depends,HTTPException,Query
import datetime
from model.post.post import Post
from sqlalchemy.orm import Session
from time import time
from services.llm_service import analyze_work
from services.post_service import generate_post
from model.summary.summary import WorkSummary
from db.session import get_db
from core.dependency import get_current_user, create_access_token
router = APIRouter(prefix="/post")

@router.post("/generate_post")
async def generate_post_route(
    work_summary_id: int,
    platform: str,
    post_length: int,
    style: str,
    inspiration: str,
    excluded_topics: list[str],
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_work_summary= db.query(WorkSummary).filter(WorkSummary.id==work_summary_id,WorkSummary.user_id==current_user.id).first()
    if not db_work_summary:
        raise HTTPException(status_code=404,detail="no work summary found")
    post = await generate_post(db_work_summary,platform,post_length,style,inspiration,excluded_topics)
    if post:
        db_post = Post(
                user_id=current_user.id,
                work_summary_id=work_summary_id,
                platform=platform,
                content=post
        )
        db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {
        "post":post
    }
