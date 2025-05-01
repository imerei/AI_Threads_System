# agents/content_agent.py

from openai import OpenAI
from utils.gpt_parser import safe_request
import time

class ContentAgent:
    def __init__(self, client: OpenAI):
        self.client = client
        self.system_instruction = (
            "You are an AI content creator writing concise, engaging Threads posts about anime."
        )

    def create_posts(self, topics: list[str]) -> list[str]:
        posts = []
        for topic in topics:
            response = safe_request(
                self.client.responses.create,
                model="gpt-4o-mini",
                fallback_model="gpt-3.5-turbo",
                max_retries=5,
                input=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user",   "content": f"Write a short Threads post about '{topic}', include 1–2 hashtags."}
                ]
            )
            # Extract assistant message
            text = next(
                evt.content[0].text
                for evt in response.output
                if evt.type == "message" and evt.role == "assistant"
            )
            posts.append(text.strip())
            # Throttle to avoid exceeding 3 requests per minute
            time.sleep(20)
        return posts
