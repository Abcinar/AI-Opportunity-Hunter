"""
Hacker News Fetcher
Front page + Show HN + Ask HN çeker.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict


def _parse_hn_page(url: str, limit: int = 15) -> List[Dict]:
    posts = []
    try:
        headers = {"User-Agent": "AIOpportunityHunter/1.0"}
        response = requests.get(url, headers=headers, timeout=15)
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
                href = title_tag.get("href", "")

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

                posts.append({
                    "source": "hacker_news",
                    "title": title,
                    "url": href if href.startswith("http") else f"https://news.ycombinator.com/{href}",
                    "points": points,
                    "comments": comments,
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception:
                continue
    except Exception as e:
        print(f"  HN fetch hatası ({url}): {e}")

    return posts


def fetch_hacker_news(limit: int = 20) -> List[Dict]:
    """Front page + Show + Ask birleştirir."""
    front = _parse_hn_page("https://news.ycombinator.com/", limit=10)
    show = _parse_hn_page("https://news.ycombinator.com/show", limit=8)
    ask = _parse_hn_page("https://news.ycombinator.com/ask", limit=8)

    # Birleştir, tekrarları temizle
    seen = set()
    merged = []
    for post in front + show + ask:
        key = post["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            merged.append(post)

    merged.sort(key=lambda x: (x.get("points", 0), x.get("comments", 0)), reverse=True)
    return merged[:limit]


if __name__ == "__main__":
    import json
    results = fetch_hacker_news(12)
    print(json.dumps(results, indent=2, ensure_ascii=False))
