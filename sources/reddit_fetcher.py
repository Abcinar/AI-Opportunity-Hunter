"""
Reddit Fetcher - Codespaces uyumlu versiyon
"""

import requests
from datetime import datetime
from typing import List, Dict


SUBREDDITS = ["indiehackers", "SaaS", "startups", "sideproject"]


def fetch_reddit_posts(limit: int = 10) -> List[Dict]:
    posts = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    per_sub = max(2, limit // len(SUBREDDITS))

    for sub in SUBREDDITS:
        try:
            # old.reddit.com bazen engeli aşar
            url = f"https://old.reddit.com/r/{sub}/hot.json?limit={per_sub}"
            response = requests.get(url, headers=headers, timeout=12)
            
            if response.status_code == 403:
                print(f"  Reddit ({sub}) engellendi (403)")
                continue
                
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

    posts.sort(key=lambda x: x.get("score", 0), reverse=True)
    return posts[:limit]


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_reddit_posts(6), indent=2, ensure_ascii=False))
