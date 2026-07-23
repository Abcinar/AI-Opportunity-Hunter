"""
Hacker News Fetcher
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict


def fetch_hacker_news(limit: int = 20) -> List[Dict]:
    posts = []
    try:
        headers = {"User-Agent": "AIOpportunityHunter/1.0"}
        response = requests.get(
            "https://news.ycombinator.com/",
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".athing")

        for item in items[:limit]:
            try:
                title_span = item.find("span", class_="titleline")
                if not title_span or not title_span.find("a"):
                    continue

                title_tag = title_span.find("a")
                title = title_tag.get_text().strip()
                url = title_tag.get("href", "")

                subtext_row = item.find_next_sibling("tr")
                points = 0
                comments = 0

                if subtext_row:
                    subtext = subtext_row.find("td", class_="subtext")
                    if subtext:
                        text = subtext.get_text()
                        points_match = re.search(r"(\d+)\s+point", text)
                        if points_match:
                            points = int(points_match.group(1))
                        comments_match = re.search(r"(\d+)\s+comment", text)
                        if comments_match:
                            comments = int(comments_match.group(1))

                post = {
                    "source": "hacker_news",
                    "title": title,
                    "url": url if url.startswith("http") else f"https://news.ycombinator.com/{url}",
                    "points": points,
                    "comments": comments,
                    "fetched_at": datetime.now().isoformat(),
                }
                posts.append(post)
            except Exception:
                continue

    except Exception as e:
        print(f"  Hacker News fetch hatası: {e}")

    return posts[:limit]


if __name__ == "__main__":
    import json
    results = fetch_hacker_news(5)
    print(json.dumps(results, indent=2, ensure_ascii=False))
