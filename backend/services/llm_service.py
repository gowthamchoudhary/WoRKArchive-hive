import httpx
from fastapi import HTTPException
from core.config import settings

import json
from model.summary.summary import WorkSummary
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
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model":settings.GROQ_MODEL,
        "messages":[
            {
                "role":"system",
                "content":""""You are a work analysis assistant.

Analyze the developer activity provided by the user.
Return ONLY JSON valid  in this  exact structure:
{
"summary": "short description of the work",
    "projects": [],
    "technologies": [],
    "activities": [],
    "accomplishments": [],
    "problems_solved": []

}

Rules:
- Only use information supported by the activity.
- Do not invent technologies, projects, or accomplishments.
- Ignore meaningless activity.
- Keep each array concise.
                """
            },
            {
                "role":"user",
                "content":json.dumps(activities_data ,indent=2)
            }
        ]
    }
    print("MODEL:", settings.GROQ_MODEL)
    print("URL:", url)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            headers=headers,
            json=payload
        )   
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    response.raise_for_status()


    data = response.json()
    content =  data["choices"][0]["message"]["content"]
    return json.loads(content)
