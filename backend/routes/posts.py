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
import json
router = APIRouter(prefix="/post",tags=["post"])

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
    work_summary_data = {
    "summary": db_work_summary.summary,
    "projects": db_work_summary.projects,
    "technologies": db_work_summary.technologies,
    "activities": db_work_summary.activities,
    "accomplishments": db_work_summary.accomplishments,
    "problems_solved": db_work_summary.problems_solved,
}

    post = await generate_post(
            work_summary_data,
            platform,
            post_length,
            style,
            inspiration,
            excluded_topics
        )

    db_post = Post(
            user_id=current_user.id,
            work_summary_id=work_summary_id,
            platform=platform,
            content=post["post"]
        )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {
        "post":post["post"]
    }


@router.get("/retrieve_posts/{worksummary_id}")
def retrieve_posts(
    worksummary_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_posts = (
        db.query(Post)
        .filter(
            Post.user_id == current_user.id,
            Post.work_summary_id == worksummary_id
        )
        .order_by(Post.created_at.desc())
        .all()
    )

    return [
        {
            "id": post.id,
            "work_summary_id": post.work_summary_id,
            "platform": post.platform,
            "content": post.content,
            "created_at": post.created_at,
            "posted_at": post.posted_at
        }
        for post in db_posts
    ]