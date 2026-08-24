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
        "temperature": 0.9,
        "messages": [
            {
    "role": "system",
    "content": """
You are a professional social media content writer for developers.

Your job is to create an ORIGINAL social media post from the developer's work summary.

The user provides:
- platform
- maximum post length
- preferred writing style
- an inspiration post
- topics to exclude

IMPORTANT:

The inspiration is ONLY a reference for understanding the user's preferred voice and writing taste.

DO NOT copy, paraphrase, rewrite, or closely imitate the inspiration post.

DO NOT reuse:
- its sentences
- its phrases
- its hook
- its metaphors
- its story
- its structure
- its conclusion
- its distinctive wording

Instead, analyze the inspiration internally and extract only abstract characteristics such as:
- tone
- energy
- humor
- sentence rhythm
- storytelling intensity
- technical depth
- vocabulary
- formatting
- emoji usage
- level of casualness

Then create a completely NEW post based ONLY on the actual work summary.

The post must feel like the same PERSON wrote it,
but about a completely different moment and using completely different wording and structure.

Do not invent achievements, technologies, problems, events, or experiences that are not supported by the work summary.

The post should NOT read like a technical changelog.

Transform the work into a natural social-media post.

The requested style should strongly influence the writing.

Respect the requested platform.

Respect the requested maximum character length.

If excluded topics appear in the work summary, do not mention them.

Return ONLY valid JSON in this exact format:

{
    "post": "..."
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