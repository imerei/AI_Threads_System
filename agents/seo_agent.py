# agents/seo_agent.py

from openai import OpenAI
from utils.gpt_parser import safe_request

class SEOAgent:
    def __init__(self, client: OpenAI, banned: list[str]):
        self.client = client
        # Normalize banned phrases for case-insensitive matching
        self.banned = [bp.lower() for bp in banned]
        ban_list = ", ".join(f'"{w}' for w in banned)
        self.system_instruction = (
            "You are an SEO expert and copywriter specializing in concise social media posts."
            " Take the user-provided draft and reword it so that:"
            " 1) It is no more than 280 characters (including spaces and punctuation)."
            " 2) It preserves the original meaning, tone."
            " 3) Add the most effective hashtag."
            " 4) It reads clearly and uses SEO-friendly language."
            f" 5) It does NOT include any of: {ban_list}.\n"
            " Respond with only the rewritten post."
        )

    def _contains_banned(self, text: str) -> bool:
        """
        Check if the text contains any banned phrase (case-insensitive).
        """
        lowered = text.lower()
        return any(b in lowered for b in self.banned)

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
            text = ""
            # Attempt up to 3 generations if banned content detected
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

                if not self._contains_banned(text):
                    break

            optimized.append(text)

        return optimized

