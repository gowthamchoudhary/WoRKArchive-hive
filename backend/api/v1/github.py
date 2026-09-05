from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from db.session import get_db
from core.dependency import get_current_user, create_access_token
from core.config import settings

from model.connections.connection import Connection
from model.activity import Activity
from model.summary.summary import WorkSummary

from services.github_service import (
    get_github_login_url,
    exchange_code_for_access_token,
    get_github_user_info,
    get_github_user_email,
    get_user_events,
    clean_relevant_events,
    normalize_github_activity,
    save_activities,
)

from services.llm_service import analyze_work


router = APIRouter(
    prefix="/api/v1/auth/github",
    tags=["Authentication"],
)


# ============================================================
# GITHUB LOGIN
# ============================================================

@router.get("/login")
async def login_github():

    github_url = await get_github_login_url()

    return RedirectResponse(github_url)


# ============================================================
# GITHUB CALLBACK
# ============================================================

@router.get("/callback")
async def github_callback(
    code: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Exchange GitHub authorization code for access token
    # --------------------------------------------------------

    access_token = await exchange_code_for_access_token(code)

    provider = "github"

    # --------------------------------------------------------
    # Get GitHub user information
    # --------------------------------------------------------

    github_user = await get_github_user_info(access_token)

    github_user_emails = await get_github_user_email(
        access_token
    )

    github_provider_user_id = str(
        github_user["id"]
    )

    # --------------------------------------------------------
    # Find existing GitHub connection for THIS user
    # --------------------------------------------------------

    db_connection = (
        db.query(Connection)
        .filter(
            Connection.user_id == current_user.id,
            Connection.provider_user_id
            == github_provider_user_id,
            Connection.provider == "github",
        )
        .first()
    )

    # --------------------------------------------------------
    # Find primary verified GitHub email
    # --------------------------------------------------------

    email = None

    for item in github_user_emails:

        if (
            item.get("primary")
            and item.get("verified")
        ):
            email = item["email"]
            break

    # --------------------------------------------------------
    # Update existing connection
    # --------------------------------------------------------

    if db_connection:

        db_connection.provider_user_id = (
            github_provider_user_id
        )

        db_connection.username = github_user["login"]

        db_connection.avatar_url = (
            github_user["avatar_url"]
        )

        db_connection.profile_url = (
            github_user["html_url"]
        )

        db_connection.access_token = access_token

        db_connection.email = email

    # --------------------------------------------------------
    # Create new connection
    # --------------------------------------------------------

    else:

        db_connection = Connection(
            user_id=current_user.id,
            provider=provider,
            provider_user_id=github_provider_user_id,
            username=github_user["login"],
            avatar_url=github_user["avatar_url"],
            profile_url=github_user["html_url"],
            access_token=access_token,
            email=email,
        )

        db.add(db_connection)

    # --------------------------------------------------------
    # Save GitHub connection
    # --------------------------------------------------------

    db.commit()

    db.refresh(db_connection)

    # --------------------------------------------------------
    # Create LOGS JWT
    # --------------------------------------------------------

    jwt_token = create_access_token(
        {
            "sub": str(current_user.id),
        }
    )

    # --------------------------------------------------------
    # Redirect back to React dashboard
    # --------------------------------------------------------

    response = RedirectResponse(
        url=f"{settings.FRONTEND_URL.rstrip('/')}/dashboard"
    )

    # --------------------------------------------------------
    # Set authentication cookie
    #
    # secure=False because we are developing on localhost.
    # Change to True when deployed with HTTPS.
    # --------------------------------------------------------

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return response


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout():

    response = RedirectResponse("/")

    response.delete_cookie(
        key="access_token"
    )

    return response


# ============================================================
# GET CONNECTED GITHUB USER
# ============================================================

@router.get("/me")
def get_github_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    user_id = current_user.id

    db_github = (
        db.query(Connection)
        .filter(
            Connection.user_id == user_id,
            Connection.provider == "github",
        )
        .first()
    )

    if not db_github:

        raise HTTPException(
            status_code=401,
            detail="User's GitHub info is not found",
        )

    return {
        "username": db_github.username,
        "email": db_github.email,
        "avatar_url": db_github.avatar_url,
        "profile_url": db_github.profile_url,
        "provider": db_github.provider,
    }


# ============================================================
# GET TODAY'S GITHUB ACTIVITY
# ============================================================

@router.get("/activity/today")
async def get_github_activity(
    post_time: time,
    timezone: str = Query("Asia/Kolkata"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Get GitHub connection
    # --------------------------------------------------------

    db_github = (
        db.query(Connection)
        .filter(
            Connection.user_id == current_user.id,
            Connection.provider == "github",
        )
        .first()
    )

    if not db_github:

        raise HTTPException(
            status_code=404,
            detail="No GitHub info is found",
        )

    access_token = db_github.access_token

    # --------------------------------------------------------
    # Get GitHub events
    # --------------------------------------------------------

    events = await get_user_events(
        db_github.username,
        access_token,
    )

    # --------------------------------------------------------
    # Timezone
    # --------------------------------------------------------

    try:

        user_timezone = ZoneInfo(timezone)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid timezone",
        )

    # --------------------------------------------------------
    # Calculate 24-hour window
    # --------------------------------------------------------

    now = datetime.now(user_timezone)

    window_end = datetime.combine(
        now.date(),
        post_time,
        user_timezone,
    )

    if window_end > now:

        window_end -= timedelta(days=1)

    window_start = (
        window_end - timedelta(hours=24)
    )

    # --------------------------------------------------------
    # Filter relevant GitHub events
    # --------------------------------------------------------

    relevant_events = []

    for event in events:

        event_time = datetime.fromisoformat(
            event["created_at"].replace(
                "Z",
                "+00:00",
            )
        )

        event_time = event_time.astimezone(
            user_timezone
        )

        if (
            window_start
            <= event_time
            <= window_end
        ):

            relevant_events.append(event)

    # --------------------------------------------------------
    # Clean GitHub events
    # --------------------------------------------------------

    git_info = await clean_relevant_events(
        relevant_events,
        access_token,
    )

    # --------------------------------------------------------
    # Debug output
    # --------------------------------------------------------

    for event in relevant_events:

        print(
            event.get("type"),
            event.get("created_at"),
        )

    # --------------------------------------------------------
    # Return activity information
    # --------------------------------------------------------

    return {
        "window": {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
        },
        "count": len(relevant_events),
        "git_info": git_info,
    }


# ============================================================
# SYNC GITHUB ACTIVITY TO DATABASE
# ============================================================

@router.post("/activity/sync")
async def sync_github_activity(
    post_time: time,
    timezone: str = Query("Asia/Kolkata"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Get GitHub connection
    # --------------------------------------------------------

    db_github = (
        db.query(Connection)
        .filter(
            Connection.user_id == current_user.id,
            Connection.provider == "github",
        )
        .first()
    )

    if not db_github:

        raise HTTPException(
            status_code=404,
            detail="No GitHub info is found",
        )

    access_token = db_github.access_token

    # --------------------------------------------------------
    # Get GitHub events
    # --------------------------------------------------------

    events = await get_user_events(
        db_github.username,
        access_token,
    )

    # --------------------------------------------------------
    # Timezone
    # --------------------------------------------------------

    try:

        user_timezone = ZoneInfo(timezone)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid timezone",
        )

    # --------------------------------------------------------
    # Calculate 24-hour window
    # --------------------------------------------------------

    now = datetime.now(user_timezone)

    window_end = datetime.combine(
        now.date(),
        post_time,
        user_timezone,
    )

    if window_end > now:

        window_end -= timedelta(days=1)

    window_start = (
        window_end - timedelta(hours=24)
    )

    # --------------------------------------------------------
    # Filter relevant events
    # --------------------------------------------------------

    relevant_events = []

    for event in events:

        event_time = datetime.fromisoformat(
            event["created_at"].replace(
                "Z",
                "+00:00",
            )
        )

        event_time = event_time.astimezone(
            user_timezone
        )

        if (
            window_start
            <= event_time
            < window_end
        ):

            relevant_events.append(event)

    # --------------------------------------------------------
    # Clean events
    # --------------------------------------------------------

    git_info = await clean_relevant_events(
        relevant_events,
        access_token,
    )

    # --------------------------------------------------------
    # Normalize activity
    # --------------------------------------------------------

    normalized_github_info = (
        normalize_github_activity(git_info)
    )

    # --------------------------------------------------------
    # Save activities
    # --------------------------------------------------------

    save_activities(
        normalized_github_info,
        current_user.id,
        db,
    )

    return {
        "activities": normalized_github_info
    }


# ============================================================
# RETRIEVE ACTIVITIES FROM DATABASE
# ============================================================

@router.get("/retrieve_activity")
async def get_activities(
    post_time: time,
    timezone: str = Query("Asia/Kolkata"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Get user's activities
    # --------------------------------------------------------

    db_activity = (
        db.query(Activity)
        .filter(
            Activity.user_id
            == current_user.id
        )
        .all()
    )

    # --------------------------------------------------------
    # Timezone
    # --------------------------------------------------------

    try:

        user_timezone = ZoneInfo(timezone)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid timezone",
        )

    # --------------------------------------------------------
    # Calculate 24-hour window
    # --------------------------------------------------------

    now = datetime.now(user_timezone)

    window_end = datetime.combine(
        now.date(),
        post_time,
        user_timezone,
    )

    if window_end > now:

        window_end -= timedelta(days=1)

    window_start = (
        window_end - timedelta(hours=24)
    )

    # --------------------------------------------------------
    # Filter activities
    # --------------------------------------------------------

    activities = []

    for activity in db_activity:

        if (
            window_start
            <= activity.occurred_at
            < window_end
        ):

            activities.append(activity)

    return activities


# ============================================================
# GENERATE WORK SUMMARY USING LLM
# ============================================================

@router.get("/retrieve_summary_llm")
async def retrieve_summary(
    post_time: time,
    timezone: str = Query("Asia/Kolkata"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Get user's activities
    # --------------------------------------------------------

    db_activity = (
        db.query(Activity)
        .filter(
            Activity.user_id
            == current_user.id
        )
        .all()
    )

    # --------------------------------------------------------
    # Timezone
    # --------------------------------------------------------

    try:

        user_timezone = ZoneInfo(timezone)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid timezone",
        )

    # --------------------------------------------------------
    # Calculate same 24-hour window
    #
    # IMPORTANT:
    # This intentionally does NOT use last_post.
    # The dashboard's post time defines the window.
    # --------------------------------------------------------

    now = datetime.now(user_timezone)

    window_end = datetime.combine(
        now.date(),
        post_time,
        user_timezone,
    )

    if window_end > now:

        window_end -= timedelta(days=1)

    window_start = (
        window_end - timedelta(hours=24)
    )

    # --------------------------------------------------------
    # Collect activities inside the window
    # --------------------------------------------------------

    activities = []

    for activity in db_activity:

        if (
            window_start
            <= activity.occurred_at
            < window_end
        ):

            activities.append(activity)

    print(
        f"SUMMARY ACTIVITIES: {len(activities)}"
    )

    # --------------------------------------------------------
    # Analyze work with LLM
    # --------------------------------------------------------

    llm_summary = await analyze_work(
        activities
    )

    # --------------------------------------------------------
    # Save WorkSummary
    # --------------------------------------------------------

    db_worksummary = WorkSummary(
        user_id=current_user.id,
        summary=llm_summary["summary"],
        projects=llm_summary["projects"],
        technologies=llm_summary["technologies"],
        activities=llm_summary["activities"],
        accomplishments=llm_summary["accomplishments"],
        problems_solved=llm_summary["problems_solved"],
        window_start=window_start,
        window_end=window_end,
    )

    db.add(db_worksummary)

    db.commit()

    db.refresh(db_worksummary)

    # --------------------------------------------------------
    # Return summary
    # --------------------------------------------------------

    return {
        "work_summary_id": db_worksummary.id,
        "llm_summary": llm_summary,
    }