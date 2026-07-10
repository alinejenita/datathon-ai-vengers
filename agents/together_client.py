import os
from openai import OpenAI
from dotenv import load_dotenv

def call_together(system_prompt, user_prompt, model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", max_tokens=1500):
    try:
        load_dotenv(override=True)
        API_KEY = os.getenv("TOGETHER_AI_API_KEY")
        if not API_KEY:
            return {"error": "TOGETHER_AI_API_KEY not found in .env"}
            
        client = OpenAI(api_key=API_KEY, base_url="https://api.together.xyz/v1")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.6
        )
        return {"message": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
