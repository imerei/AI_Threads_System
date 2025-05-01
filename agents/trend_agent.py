"""
agents/trend_agent.py

TrendAgent: Aggregates and logs trending anime topics via the Responses API,
stores full lists to Excel, and delivers only the top topic for subsequent agents.
"""

import os
import time
import json
from datetime import datetime

import pandas as pd
from openai import OpenAI
from utils.gpt_parser import safe_request


class TrendAgent:
    def __init__(self, client: OpenAI, excel_path: str = "data/anime_trends.xlsx"):
        """
        Initialize TrendAgent.

        Args:
            client: OpenAI Responses API client.
            excel_path: Path to Excel file for logging all fetched topics.
        """
        self.client = client
        self.excel_path = excel_path

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)

    def fetch_trending_topics(self) -> list[str]:
        """
        Calls the Responses API’s web_search tool to retrieve up-to-date trending anime topics.

        Returns:
            A list of topic strings in the order returned by the API.
        """
        response = safe_request(
            self.client.responses.create,
            model="gpt-4o-mini",
            fallback_model="gpt-3.5-turbo",
            max_retries=5,
            input="Find the current top 5 trending anime topics",
            tools=[{"type": "web_search"}]
        )

        # Extract assistant’s message
        raw = None
        for event in response.output:
            if event.type == "message" and event.role == "assistant":
                raw = event.content[0].text
                break
        if raw is None:
            raise Exception("No assistant message returned from web_search")

        # Parse JSON array or fallback to line splitting
        try:
            topics = json.loads(raw)
        except json.JSONDecodeError:
            topics = [line.strip("- ") for line in raw.splitlines() if line.strip()]

        return topics

    def _log_topics_to_excel(self, topics: list[str]) -> None:
        """
        Append all fetched topics with timestamps to the configured Excel file.

        Args:
            topics: List of raw topic strings.
        """
        now = datetime.now()
        df_new = pd.DataFrame({
            "timestamp": [now] * len(topics),
            "topic": topics
        })

        try:
            df_existing = pd.read_excel(self.excel_path, engine="openpyxl")
            df = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df = df_new

        # Write back to Excel
        df.to_excel(self.excel_path, index=False, engine="openpyxl")

    def get_top_topics(self) -> list[str]:
        """
        Fetch trends, log the full list to Excel, and return only the first topic.

        Returns:
            A single-element list containing the top trending topic, or empty list if none.
        """
        topics = self.fetch_trending_topics()
        if not topics:
            return []

        # Log all topics
        self._log_topics_to_excel(topics)

        # Deliver only the first topic
        return [topics[0]]
