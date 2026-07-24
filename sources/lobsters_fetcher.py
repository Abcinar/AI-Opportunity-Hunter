"""
Lobsters (lobste.rs) Fetcher
HN benzeri kaliteli teknik sinyal kaynağı.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict


def fetch_lobsters(limit: int = 10) -> List[Dict]:
    posts = []
    try:
        headers = {"User-Agent": "AIOpportunityHunter/1.0"}
        response = requests.get("https://lobste.rs/", headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        stories = soup.select(".story")
        for story in stories[:limit]:
            try:
                link = story.select_one(".u-url")
                if not link:
                    continue
                title = link.get_text().strip()
                url = link.get("href", "")
                if url.startswith("/"):
                    url = "https://lobste.rs" + url

                score_el = story.select_one(".score")
                points = int(score_el.get_text().strip()) if score_el else 0

                comments_el = story.select_one(".comments_label a")
                comments = 0
                if comments_el:
                    txt = comments_el.get_text()
                    if "comment" in txt:
                        comments = int("".join(filter(str.isdigit, txt)) or 0)

                posts.append({
                    "source": "lobsters",
                    "title": title,
                    "url": url,
                    "points": points,
                    "comments": comments,
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception:
                continue
    except Exception as e:
        print(f"  Lobsters fetch hatası: {e}")

    return posts[:limit]


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_lobsters(5), indent=2, ensure_ascii=False))
