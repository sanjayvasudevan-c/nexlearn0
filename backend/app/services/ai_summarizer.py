import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_text(topic: str, text: str):

    prompt = f"""
    Generate structured academic notes for the topic: {topic}

    Format:
    1. Definition
    2. Key concepts
    3. Important points
    4. Examples
    5. Summary

    Source text:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content