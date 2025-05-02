# agents/seo_agent.py

from openai import OpenAI
from utils.gpt_parser import safe_request

class SEOAgent:
    def __init__(self, client: OpenAI, max_length: int = 280):
        self.client = client
        self.max_length = max_length
        self.system_instruction = (
            "You are an SEO expert and copywriter specializing in concise social media posts."
            " Take the user-provided draft and reword it so that:"
            " 1) It is no more than 280 characters (including spaces and punctuation)."
            " 2) It preserves the original meaning, tone, and all existing hashtags."
            " 3) It reads clearly and uses SEO-friendly language."
            " Respond with only the rewritten post."
        )

    def optimize_posts(self, drafts: list[str]) -> list[str]:
        optimized = []
        for draft in drafts:
            messages = [
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": f"Here is the draft to optimize:\n\n{draft}"}
            ]

            response = safe_request(
                self.client.responses.create,
                model="gpt-4o-mini",
                fallback_model="gpt-3.5-turbo",
                max_retries=5,
                input=messages
            )

            # Extract assistant reply
            text = next(
                evt.content[0].text
                for evt in response.output
                if evt.type == "message" and evt.role == "assistant"
            ).strip()

            optimized.append(text)

        return optimized

