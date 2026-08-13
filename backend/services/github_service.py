import httpx
from fastapi import HTTPException
from core.config import settings


async def get_github_login_url():
    return (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=read:user user:email"
    )


async def exchange_code_for_access_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

    token_data = response.json()

    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="Failed to get GitHub access token",
        )

    return access_token


async def get_github_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch GitHub user",
        )

    return response.json()
async def get_github_user_email(access_token:str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="failed to fetch the user email"
            )
    return response.json()


async def get_user_events(username:str,access_token:str):
    headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {access_token}",
    "X-GitHub-Api-Version": "2022-11-28",
}
    async with httpx.AsyncClient() as client:
        response = await client.get(
               f"https://api.github.com/users/{username}/events",
               headers=headers,
               params={
                   "per_page":100,
                   "page":1
               }
        )
        response.raise_for_status()
        return response.json()
def clean_relevant_events(events):
    allowed_EVENTS = {
    "PushEvent",
    "PullRequestEvent",
    "IssuesEvent",
    "IssueCommentEvent",
    "PullRequestReviewEvent",
    "PullRequestReviewCommentEvent",
    "ReleaseEvent",
}
    relevent_events=[]
    for event in events:
        event_type = event.get("type")
        if event_type  in allowed_EVENTS:
            relevent_events.append(event)
    return relevent_events
