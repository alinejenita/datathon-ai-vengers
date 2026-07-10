import os
from openai import OpenAI
from dotenv import load_dotenv

def call_openrouter(system_prompt, user_prompt, model="anthropic/claude-3.5-sonnet", max_tokens=1000):
    try:
        load_dotenv(override=True)
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        if not API_KEY:
            return {"error": "OPENROUTER_API_KEY not found in .env"}
            
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        
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
