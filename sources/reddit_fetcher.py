"""
Reddit Fetcher
Public JSON endpoint kullanarak veri çeker (API key gerekmez).
"""

import requests
from datetime import datetime
from typing import List, Dict


SUBREDDITS = [
    "indiehackers",
    "SaaS",
    "startups",
    "Entrepreneur",
    "sideproject",
]


def fetch_reddit_posts(limit: int = 10) -> List[Dict]:
    """Birden fazla subreddit'ten hot post'ları çeker."""
    posts = []
    headers = {"User-Agent": "AIOpportunityHunter/1.0"}

    per_sub = max(3, limit // len(SUBREDDITS))

    for sub in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit={per_sub}"
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            data = response.json()

            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                posts.append({
                    "source": "reddit",
                    "subreddit": sub,
                    "title": post_data.get("title", ""),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "score": post_data.get("score", 0),
                    "comments": post_data.get("num_comments", 0),
                    "fetched_at": datetime.now().isoformat(),
                })
        except Exception as e:
            print(f"  Reddit ({sub}) hatası: {e}")
            continue

    # Skora göre sırala
    posts.sort(key=lambda x: x.get("score", 0), reverse=True)
    return posts[:limit]


if __name__ == "__main__":
    import json
    results = fetch_reddit_posts(8)
    print(json.dumps(results, indent=2, ensure_ascii=False))
