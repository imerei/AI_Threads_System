"""
agents/trend_agent.py

TrendAgent: Uses the OpenAI Responses API’s web_search tool to fetch
live anime trends, with retries/backoff and fallback built in.
"""

import json
import time
from openai import OpenAI
from utils.gpt_parser import safe_request


class TrendAgent:
    def __init__(self, client: OpenAI):
        """
        Args:
            client: An OpenAI client instance from Responses API (from config_loader).
        """
        self.client = client
        # Pause between calls to respect RPM limits (60s / 3 calls = 20s)
        self.throttle_seconds = 20

    def fetch_trending_topics(self) -> list[str]:
        """
        Retrieves current top anime trends via the built-in web_search tool,
        using safe_request to handle rate limits and fallbacks.
        """
        # Use safe_request to call the Responses API
        response = safe_request(
            self.client.responses.create,
            model="gpt-4o-mini",
            fallback_model="gpt-3.5-turbo",
            max_retries=5,
            input="Find the current top 10 trending anime topics",
            tools=[{"type": "web_search"}]
        )

        # Throttle to avoid RPM breaches
        time.sleep(self.throttle_seconds)

        # Extract the assistant message from the Response events
        for event in response.output:
            if event.type == "message" and event.role == "assistant":
                raw = event.content[0].text
                break
        else:
            raise Exception("No assistant message returned from web_search")

        # Parse JSON list or fallback to line-splitting
        try:
            topics = json.loads(raw)
        except json.JSONDecodeError:
            topics = [line.strip("- ") for line in raw.splitlines() if line.strip()]

        return topics

    def get_top_topics(self, limit: int = 5) -> list[str]:
        """
        Returns the top N unique topics from the fetched trend list.
        """
        topics = self.fetch_trending_topics()
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in topics:
            if t not in seen:
                seen.add(t)
                unique.append(t)
            if len(unique) >= limit:
                break
        return unique

