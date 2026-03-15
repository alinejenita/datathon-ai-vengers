import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env")

client = anthropic.Anthropic(api_key=API_KEY)

def call_claude(system_prompt, user_prompt, max_tokens=1000):
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return {"message": response.content[0].text}
    except Exception as e:
        return {"error": str(e)}