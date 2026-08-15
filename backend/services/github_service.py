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
async def clean_relevant_events(events,access_token):
    allowed_EVENTS = {
    "PushEvent",
    "PullRequestEvent",
    "IssuesEvent",
    "IssueCommentEvent",
    "PullRequestReviewEvent",
    "PullRequestReviewCommentEvent",
    "ReleaseEvent",
}
    
    
    git_info = {
  "commits": [],
  "pull_requests": [],
  "issues": [],
  "issue_comments": [],
  "reviews": [],
  "review_comments": [],
  "releases": []
}
    for event in events:
        event_type = event.get("type")
        
        if event_type == "PushEvent":
            payload = event.get("payload")
            repo =  event.get("repo", {}).get("name")
            head = payload.get("head")
            before = payload.get("before")
            commits = []
            if before and head:
                commits = await compare_push_commits(repo=repo,access_token=access_token,head=head,before=before)
        
            for commit in commits:
                sha = commit["sha"]
                details = await get_commit_details(sha=sha,repo_name=repo,access_token=access_token)
                if details:
                    message = details.get("commit",{}).get("message")
                    date = details.get("commit",{}).get("author",{}).get("date")
                    git_info["commits"].append({
        "message": message,
        "date": date,
        "sha": sha[:7],
        "repo": repo
    })
        elif event_type=="PullRequestEvent":
            
            payload = event["payload"]
            action = payload.get("action")
            pull_request = payload.get("pull_request", {})
            title = pull_request.get("title")
            url = pull_request.get("html_url")
            number = pull_request.get("number")
            state = pull_request.get("state")
            merged = pull_request.get("merged")
            git_info["pull_requests"].append({
    "action": action,
    "title": title,
    "url": url,
    "number": number,
    "state": state,
    "merged": merged,
})
        elif event_type == "IssuesEvent":
            payload = event["payload"]

            action = payload.get("action")
            issue = payload.get("issue", {})

            title = issue.get("title")
            url = issue.get("html_url")
            number = issue.get("number")
            state = issue.get("state")
            repo = event.get("repo", {}).get("name")
            created_at = event.get("created_at")
            git_info["issues"].append({
    "action": action,
    "title": title,
    "url": url,
    "number": number,
    "state": state,
    "repo": repo,
    "created_at": created_at,
}) 
        elif event_type == "IssueCommentEvent":
            payload = event.get("payload", {})
            issue = payload.get("issue", {})
            comment = payload.get("comment", {})

            git_info["issue_comments"].append({
                "action": payload.get("action"),
                "issue_title": issue.get("title"),
                "issue_number": issue.get("number"),
                "comment_body": comment.get("body", "")[:200],  
                "url": comment.get("html_url"),
                "repo": event.get("repo", {}).get("name"),
                "created_at": event.get("created_at")
            })
        elif event_type == "PullRequestReviewEvent":
            payload = event.get("payload", {})
            pr = payload.get("pull_request", {})
            review = payload.get("review", {})

            git_info["reviews"].append({
                "action": payload.get("action"),
                "pr_title": pr.get("title"),
                "pr_number": pr.get("number"),
                "state": review.get("state"),  
                "body": review.get("body", "")[:200],
                "url": review.get("html_url"),
                "repo": event.get("repo", {}).get("name"),
                "created_at": event.get("created_at")
            })
        elif event_type == "PullRequestReviewCommentEvent":
                payload = event.get("payload", {})
                pr = payload.get("pull_request", {})
                comment = payload.get("comment", {})

                git_info["review_comments"].append({
                    "action": payload.get("action"),
                    "pr_title": pr.get("title"),
                    "pr_number": pr.get("number"),
                    "file_path": comment.get("path"),
                    "comment_body": comment.get("body", "")[:200],
                    "url": comment.get("html_url"),
                    "repo": event.get("repo", {}).get("name"),
                    "created_at": event.get("created_at")
                })
        elif event_type == "ReleaseEvent":
            payload = event.get("payload", {})
            release = payload.get("release", {})

            git_info["releases"].append({
                "action": payload.get("action"),  
                "tag_name": release.get("tag_name"),
                "name": release.get("name"),
                "body": release.get("body", "")[:300],
                "prerelease": release.get("prerelease", False),
                "url": release.get("html_url"),
                "repo": event.get("repo", {}).get("name"),
                "created_at": event.get("created_at")
            })


    return git_info
async def get_commit_details(
        repo_name:str,
        sha:str,
        access_token:str
):
    headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url = f"https://api.github.com/repos/{repo_name}/commits/{sha}",
            headers=headers,
                    )
        if response.status_code == 200:
            return response.json()
        return None
async def compare_push_commits(
        repo:str,
        before:str,
        
        access_token:str,
        head:str
):
    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url = f"https://api.github.com/repos/{repo}/compare/{before}...{head}",
            headers=headers
        )
        if response.status_code==200:
            data= response.json()
            return data.get("commits")
        return []

def normalize_github_activity(git_info):
    normalized_info = []

    for event_type, items in git_info.items():

        for item in items:

            if event_type == "commits":
                title = item.get("message")

            elif event_type == "pull_requests":
                title = item.get("title")

            elif event_type == "issues":
                title = item.get("title")

            elif event_type == "issue_comments":
                title = item.get("issue_title")

            elif event_type == "reviews":
                title = item.get("pr_title")

            elif event_type == "review_comments":
                title = item.get("pr_title")

            elif event_type == "releases":
                title = item.get("name")

            else:
                title = None

            activity = {
                "source": "github",
                "type": event_type,
                "title": title,
                "repository": item.get("repo"),
                "url": item.get("url"),
                "occurred_at": item.get("date") or item.get("created_at")
            }

            normalized_info.append(activity)

    return normalized_info