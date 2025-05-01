"""gpt_parser: Helper functions for interacting with GPT-4 and parsing outputs."""

import openai
from openai import RateLimitError
import time
import random

def ask_gpt(system_prompt: str, user_prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 150, temperature: float = 0.7):
    """
    Send a prompt to GPT-4 and return the response text.
    system_prompt: role=system message for context.
    user_prompt: role=user message for the actual request.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    text = response['choices'][0]['message']['content'].strip()
    return text

def safe_request(client_method, *, model, max_retries=6, fallback_model=None, **kwargs):
    """
    Call an OpenAI method (e.g. client.responses.create) with retries/backoff and optional model fallback.
    - client_method: function to call (e.g. client.responses.create)
    - model: primary model name (string)
    - fallback_model: if provided, model to switch to after exhausting retries
    - kwargs: other keyword args to pass to client_method
    """
    for attempt in range(max_retries):
        try:
            return client_method(model=model, **kwargs)
        except RateLimitError as e:
            wait = (2 ** attempt) + random.random()
            print(f"[RateLimit] model={model} attempt={attempt+1}/{max_retries}, retrying in {wait:.1f}s")
            time.sleep(wait)
    # If we have a fallback model, try once with that
    if fallback_model:
        print(f"[Fallback] switching to {fallback_model}")
        return client_method(model=fallback_model, **kwargs)
    # Otherwise, re-raise
    raise
