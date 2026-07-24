"""
Google Trends Fetcher
Yükselen arama trendlerini çeker (pytrends).
"""

from datetime import datetime
from typing import List, Dict

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None


# Solo founder / SaaS ile ilgili tohum kelimeler
SEED_KEYWORDS = [
    "saas",
    "indie hacker",
    "no code",
    "ai tool",
    "side project",
    "freelance tool",
    "automation",
    "chatgpt alternative",
]


def fetch_google_trends(limit: int = 10) -> List[Dict]:
    posts = []

    if TrendReq is None:
        print("  Google Trends: pytrends yuklu degil (pip install pytrends)")
        return posts

    try:
        pytrends = TrendReq(hl="en-US", tz=180, retries=2, backoff_factor=0.3)

        # Rising queries (ilgili yukselen aramalar)
        for seed in SEED_KEYWORDS[:4]:  # rate limit icin sinirli
            try:
                pytrends.build_payload([seed], timeframe="now 7-d")
                related = pytrends.related_queries()

                rising = related.get(seed, {}).get("rising")
                if rising is None or rising.empty:
                    continue

                for _, row in rising.head(3).iterrows():
                    query = str(row.get("query", "")).strip()
                    value = int(row.get("value", 0)) if row.get("value") != "Breakout" else 5000
                    if not query:
                        continue

                    posts.append({
                        "source": "google_trends",
                        "title": f"Rising: {query} (seed: {seed})",
                        "url": f"https://trends.google.com/trends/explore?q={query.replace(' ', '%20')}",
                        "points": min(value, 5000),
                        "comments": 0,
                        "fetched_at": datetime.now().isoformat(),
                    })
            except Exception:
                continue

        # Tekrarlari temizle
        seen = set()
        unique = []
        for p in posts:
            key = p["title"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(p)

        unique.sort(key=lambda x: x.get("points", 0), reverse=True)
        return unique[:limit]

    except Exception as e:
        print(f"  Google Trends hatasi: {e}")
        return []


if __name__ == "__main__":
    import json
    results = fetch_google_trends(8)
    print(f"Bulunan: {len(results)}")
    print(json.dumps(results, indent=2, ensure_ascii=False))
