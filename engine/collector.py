"""
AI Opportunity Hunter
Collector Engine

Görevi:
- Tüm veri kaynaklarından sinyal toplamak
- Tek listede birleştirmek
- Sıralamak
- main.py'ye geri döndürmek
"""

from datetime import datetime

from config import (
    GITHUB_LIMIT,
    HN_LIMIT,
    GOOGLE_LIMIT,
)

from sources.github_fetcher import fetch_github_trending
from sources.hn_fetcher import fetch_hacker_news
from sources.trends_fetcher import fetch_google_trends


class Collector:

    def __init__(self):
        self.posts = []
        self.sources = {}

    def _fetch(self, name, func, limit):
        """
        Bir kaynaktan veri çeker.
        Hata olursa sistemi durdurmaz.
        """

        try:
            print(f"▶ {name}...")

            results = func(limit=limit)

            if results is None:
                results = []

            self.posts.extend(results)

            self.sources[name] = len(results)

            print(f"   ✓ {len(results)} sinyal")

        except Exception as e:

            self.sources[name] = 0

            print(f"   ✗ {name} hatası")
            print(f"     {e}")

    def collect(self):

        print("\n========== SIGNAL COLLECTION ==========\n")

        self._fetch(
            "github_trending",
            fetch_github_trending,
            GITHUB_LIMIT,
        )

        self._fetch(
            "hacker_news",
            fetch_hacker_news,
            HN_LIMIT,
        )

        self._fetch(
            "google_trends",
            fetch_google_trends,
            GOOGLE_LIMIT,
        )

        self.posts.sort(
            key=lambda x: (
                int(x.get("points", 0) or 0),
                int(x.get("comments", 0) or 0),
            ),
            reverse=True,
        )

        return {
            "fetched_at": datetime.now().isoformat(),
            "total_signals": len(self.posts),
            "sources": self.sources,
            "posts": self.posts,
        }


def collect_all_sources():

    collector = Collector()

    return collector.collect()
