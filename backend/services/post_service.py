import httpx
from core.config import settings
import json


async def generate_post(
    work_summary,
    platform,
    post_length,
    style,
    inspiration,
    excluded_topics
):
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": """
You are a professional social media content writer.

Generate a social media post from the developer's work summary.

Requirements:
- Follow the requested platform.
- Respect the requested maximum post length.
- Match the requested writing style.
- Use the provided inspiration as a stylistic reference.
- Remove anything related to the excluded topics.
- Never invent work, technologies, projects, or accomplishments.
- Return ONLY valid JSON.

Return exactly:

{
    "post": "the final social media post"
}
"""
            },
            {
                "role": "user",
                "content": json.dumps({
                    "work_summary": work_summary,
                    "platform": platform,
                    "post_length": post_length,
                    "style": style,
                    "inspiration": inspiration,
                    "excluded_topics": excluded_topics
                })
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload
        )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    response.raise_for_status()

    data = response.json()

    content = data["choices"][0]["message"]["content"]

    return json.loads(content)