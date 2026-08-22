import httpx
from fastapi import HTTPException
from core.config import settings
from db.session import get_db   
import json

async def analyze_work(activities):
    activities_data = []
    for activity in activities:
        activities_data.append({
            "source": activity.source,
            "type": activity.type,
            "title": activity.title,
            "repository": activity.repository,
            "url": activity.url,
            "occurred_at": activity.occurred_at.isoformat()}
        )
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    url ="https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model":settings.OPENROUTER_MODEL,
        "messages":[
            {
                "role":"system",
                "content":""""You are a work analysis assistant.

Analyze the developer activity provided by the user.

Identify:
- what they worked on
- the projects involved
- important technologies
- meaningful accomplishments

Ignore meaningless activity.
Do not invent anything that is not supported by the activity.

Return a concise summary.
                """
            },
            {
                "role":"user",
                "content":json.dumps(activities_data)
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            headers=headers,
            json=payload
        )
    response.raise_for_status()
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    return None