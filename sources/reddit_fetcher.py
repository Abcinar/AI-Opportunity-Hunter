"""
Reddit Fetcher (placeholder)
API credentials eklendikten sonra aktif edilecek.
"""

from datetime import datetime
from typing import List, Dict


def fetch_reddit_posts(limit: int = 10) -> List[Dict]:
    posts = [
        {
            "source": "reddit",
            "title": "Reddit entegrasyonu hazır. API anahtarlarını .env dosyasına ekleyin.",
            "url": "https://reddit.com/r/indiehackers",
            "score": 0,
            "comments": 0,
            "fetched_at": datetime.now().isoformat(),
        }
    ]
    return posts[:limit]


if __name__ == "__main__":
    import json
    results = fetch_reddit_posts()
    print(json.dumps(results, indent=2, ensure_ascii=False))
