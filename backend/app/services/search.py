import os
import time
from typing import List
from urllib.parse import urlparse

import requests

from ..schemas import SearchResult


class RateLimiter:
    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self.events = {}

    def check(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60
        history = [t for t in self.events.get(key, []) if t > window_start]
        if len(history) >= self.max_per_minute:
            self.events[key] = history
            return False
        history.append(now)
        self.events[key] = history
        return True


rate_limiter = RateLimiter()


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def demo_results(query: str) -> List[SearchResult]:
    demo = [
        SearchResult(
            title="Example school board report",
            url="https://example.org/report",
            domain="example.org",
            snippet=f"Sample report related to '{query}'.",
            published_date="2022-05-10",
        ),
        SearchResult(
            title="Local news coverage",
            url="https://news.example.com/story",
            domain="news.example.com",
            snippet=f"News coverage mentioning '{query}' in context.",
            published_date="2023-02-01",
        ),
    ]
    return demo


def search_web(query: str) -> (str, List[SearchResult]):
    api_key = os.getenv("SEARCH_API_KEY")
    provider = os.getenv("SEARCH_PROVIDER", "serpapi")
    if not api_key:
        return "demo", demo_results(query)

    if provider == "serpapi":
        response = requests.get(
            "https://serpapi.com/search.json",
            params={"engine": "google", "q": query, "api_key": api_key},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("organic_results", [])[:5]:
            url = item.get("link")
            if not url:
                continue
            results.append(
                SearchResult(
                    title=item.get("title", "Untitled"),
                    url=url,
                    domain=_domain_from_url(url),
                    snippet=item.get("snippet", ""),
                )
            )
        return "serpapi", results

    if provider == "bing":
        response = requests.get(
            "https://api.bing.microsoft.com/v7.0/search",
            headers={"Ocp-Apim-Subscription-Key": api_key},
            params={"q": query},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("webPages", {}).get("value", [])[:5]:
            url = item.get("url")
            if not url:
                continue
            results.append(
                SearchResult(
                    title=item.get("name", "Untitled"),
                    url=url,
                    domain=_domain_from_url(url),
                    snippet=item.get("snippet", ""),
                )
            )
        return "bing", results

    return "demo", demo_results(query)
