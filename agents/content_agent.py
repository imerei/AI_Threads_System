"""
agents/content_agent.py

ContentAgent: Generates a single Threads post for a given anime topic using
OpenAI’s Responses API, enforcing rate-limit backoff and fallback logic.
"""

import time
from openai import OpenAI
from utils.gpt_parser import safe_request


class ContentAgent:
    def __init__(self, client: OpenAI, banned: list[str]):
        """
        Args:
            client: An OpenAI Responses API client instance.
        """
        self.client = client
        # Normalize banned phrases to lowercase for matching
        self.banned = [bp.lower() for bp in banned]
        ban_list = ", ".join(f'"{w}"' for w in banned)
        self.system_instruction = (
            "You are an subtly sarcastic content creator writing short, witty Threads posts about anime."
            " Your posts have to do the following:"
            " 1) Only talk about one anime series."
            " 2) If the topic has a list of anime, only talk about the highest ranking one."
            " 3) Use only one emoji and do so sparringly."
            " 4) There are no questions. Just thoughts and observations"
            f" 5) Avoid using the following words: {ban_list}.\n"
        )

    def _contains_banned(self, text: str) -> bool:
        """Check if the text contains any banned phrase (case-insensitive)."""
        lowered = text.lower()
        return any(b in lowered for b in self.banned)

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
            {"role": "user",   "content": f"Write a short Threads post about '{topic}', include 1–2 relevant hashtags. "
             "Remember to avoid using words and phrases in ban list referenced in the system instructions "
             }
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
        text = ""
        # Attempt up to 3 generations to avoid banned content
        for attempt in range(3):
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

            # If no banned phrase, accept; else retry
            if not self._contains_banned(text):
                break

        # Return the final text (may contain banned words if all retries failed)
        # Throttle to respect RPM limits
        time.sleep(60.0 / 500)
        return [text]


