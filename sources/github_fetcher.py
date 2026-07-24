"""
GitHub Trending Fetcher
Son 24 saatte yükselen repoları çeker.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict


def fetch_github_trending(limit: int = 10, since: str = "daily") -> List[Dict]:
    posts = []
    try:
        headers = {"User-Agent": "AIOpportunityHunter/1.0"}
        url = f"https://github.com/trending?since={since}"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.select("article.Box-row")
        for article in articles[:limit]:
            try:
                h2 = article.select_one("h2 a")
                if not h2:
                    continue
                repo_path = h2.get("href", "").strip()
                title = repo_path.strip("/")
                url = "https://github.com" + repo_path

                desc_el = article.select_one("p")
                description = desc_el.get_text().strip() if desc_el else ""

                stars_el = article.select_one("span.d-inline-block.float-sm-right")
                stars_today = 0
                if stars_el:
                    txt = stars_el.get_text().strip().replace(",", "")
                    digits = "".join(filter(str.isdigit, txt))
                    stars_today = int(digits) if digits else 0

                posts.append({
                    "source": "github_trending",
                    "title": f"{title} — {description}" if description else title,
                    "url": url,
                    "points": stars_today,
                    "comments": 0,
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception:
                continue
    except Exception as e:
        print(f"  GitHub Trending hatası: {e}")

    return posts[:limit]


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_github_trending(5), indent=2, ensure_ascii=False))
