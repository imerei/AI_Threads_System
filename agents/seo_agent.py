# agents/seo_agent.py

from openai import OpenAI
from utils.gpt_parser import safe_request

class SEOAgent:
    def __init__(self, client: OpenAI, max_length: int = 280):
        self.client = client
        self.max_length = max_length
        self.system_instruction = "You are an SEO specialist optimizing social media posts."

    def optimize_posts(self, drafts: list[str]) -> list[str]:
        optimized = []
        for draft in drafts:
            response = safe_request(
                self.client.responses.create,
                model="gpt-4o-mini",
                fallback_model="gpt-3.5-turbo",
                max_retries=5,
                input=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user",   "content":
                        f"Optimize this post (under {self.max_length} chars) for clarity, engagement, and hashtags:\n\n{draft}"
                    }
                ]
            )
            text = next(
                evt.content[0].text
                for evt in response.output
                if evt.type == "message" and evt.role == "assistant"
            ).strip()
            # Enforce hard cutoff
            if len(text) > self.max_length:
                text = text[: self.max_length -1] + "…"
            optimized.append(text)
        return optimized

