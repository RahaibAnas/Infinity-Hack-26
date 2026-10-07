import os

from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

with OpenRouter(api_key=api_key) as client:
    response = client.chat.send(
        model="openrouter/auto",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: OpenRouter connection works.",
            }
        ],
    )

    print(response.choices[0].message.content)
