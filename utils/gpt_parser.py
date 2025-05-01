"""gpt_parser: Helper functions for interacting with GPT-4 and parsing outputs."""

import openai
from openai import RateLimitError
import time
import random

# Default requests per limit for throttling
DEFAULT_RPM_LIMIT = 500

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

def safe_request(
    client_method,
    *,
    model: str,
    max_retries: int = 6,
    fallback_model: str | None = None,
    rpm_limit: int = DEFAULT_RPM_LIMIT,
    **kwargs
):
    """
    Call an OpenAI method (e.g. client.responses.create) with retries, exponential backoff,
    optional model fallback, and throttling to respect RPM limits.

    Args:
        client_method: The OpenAI client method to invoke.
        model: Primary model name to use.
        max_retries: Number of retry attempts on RateLimitError.
        fallback_model: Alternate model to use if retries are exhausted.
        rpm_limit: Requests-per-minute limit for throttling.
        **kwargs: Additional keyword args to pass to the client method.

    Returns:
        The response from the OpenAI API.
    """
    # Compute throttle interval (seconds between requests)
    throttle_seconds = 60.0 / rpm_limit if rpm_limit > 0 else 0

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client_method(model=model, **kwargs)
            # Throttle to respect RPM cap
            if throttle_seconds:
                time.sleep(throttle_seconds)
            return response
        except RateLimitError as e:
            last_error = e
            wait_time = (2 ** attempt) + random.random()
            print(
                f"[RateLimit] model={model} attempt {attempt+1}/{max_retries}, "
                f"retrying in {wait_time:.1f}s..."
            )
            time.sleep(wait_time)

    # If fallback model is provided, try once using it
    if fallback_model:
        print(f"[Fallback] switching to model {fallback_model}")
        response = client_method(model=fallback_model, **kwargs)
        if throttle_seconds:
            time.sleep(throttle_seconds)
        return response

    # If all retries failed without fallback, raise the last encountered error
    raise last_error
