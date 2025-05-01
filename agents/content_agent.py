"""
agents/content_agent.py

ContentAgent: Generates a single Threads post for a given anime topic using
OpenAI’s Responses API, enforcing rate-limit backoff and fallback logic.
"""

from openai import OpenAI
from utils.gpt_parser import safe_request


class ContentAgent:
    def __init__(self, client: OpenAI):
        """
        Args:
            client: An OpenAI Responses API client instance.
        """
        self.client = client
        self.system_instruction = (
            "You are an AI content creator writing concise, engaging Threads posts about anime."
        )

    def create_posts(self, topic: str) -> list[str]:
        """
        Generate a single Threads post for the provided topic.

        Args:
            topic: The anime topic to create a post about.

        Returns:
            A list containing the single generated post string.
        """
        # Build conversation messages
        messages = [
            {"role": "system", "content": self.system_instruction},
            {"role": "user",   "content": f"Write a short Threads post about '{topic}', include 1–2 relevant hashtags."}
        ]

        # Request completion with backoff and fallback
        response = safe_request(
            self.client.responses.create,
            model="gpt-4o-mini",
            fallback_model="gpt-3.5-turbo",
            max_retries=5,
            input=messages
        )

        # Extract assistant's reply
        text = next(
            evt.content[0].text
            for evt in response.output
            if evt.type == "message" and evt.role == "assistant"
        ).strip()

        return [text]


