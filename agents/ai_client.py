import os
from typing import Dict, Any, Optional
from agents.groq_client import call_groq
from agents.openrouter_client import call_openrouter
from agents.openai_client import call_openai

def call_ai_with_fallback(
    system_prompt: str, 
    user_prompt: str, 
    primary_model: str = "llama-3.3-70b-versatile",
    fallback_model: str = "anthropic/claude-3.5-sonnet",
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Unified AI client that tries Groq first, then falls back to OpenRouter, then OpenAI.
    Returns the first successful response.
    """
    
    # Try Groq first
    print("[AI] Attempting Groq (primary)...")
    groq_response = call_groq(system_prompt, user_prompt, model=primary_model, max_tokens=max_tokens)
    if "error" not in groq_response and groq_response.get("message"):
        print("[AI] Groq successful")
        return {"provider": "groq", "message": groq_response["message"]}
    else:
        print(f"[AI] Groq failed: {groq_response.get('error', 'Unknown error')}")
    
    # Fallback to OpenRouter
    print("[AI] Attempting OpenRouter (fallback)...")
    openrouter_response = call_openrouter(system_prompt, user_prompt, model=fallback_model, max_tokens=max_tokens)
    if "error" not in openrouter_response and openrouter_response.get("message"):
        print("[AI] OpenRouter successful")
        return {"provider": "openrouter", "message": openrouter_response["message"]}
    else:
        print(f"[AI] OpenRouter failed: {openrouter_response.get('error', 'Unknown error')}")
    
    # Final fallback to OpenAI
    print("[AI] Attempting OpenAI (final fallback)...")
    openai_response = call_openai(system_prompt, user_prompt, model="gpt-4o", max_tokens=max_tokens)
    if "error" not in openai_response and openai_response.get("message"):
        print("[AI] OpenAI successful")
        return {"provider": "openai", "message": openai_response["message"]}
    else:
        print(f"[AI] OpenAI failed: {openai_response.get('error', 'Unknown error')}")
    
    # All providers failed
    return {
        "error": "All AI providers failed",
        "details": {
            "groq": groq_response.get("error", "Unknown error"),
            "openrouter": openrouter_response.get("error", "Unknown error"),
            "openai": openai_response.get("error", "Unknown error")
        }
    }

def call_ai_simple(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
    """
    Simple wrapper that returns just the message string or raises an exception.
    """
    response = call_ai_with_fallback(system_prompt, user_prompt, max_tokens=max_tokens)
    if "error" in response:
        raise Exception(f"AI providers failed: {response['error']}")
    return response["message"]
