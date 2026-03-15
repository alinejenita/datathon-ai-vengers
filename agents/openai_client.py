import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

def call_openai(system_prompt, user_prompt, model="gpt-4o", max_tokens=1000):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0
        )
        return {"message": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
