"""
Product Hunt Fetcher
Bugünün ürünlerini çeker (scrape, API key gerekmez).
"""

import requests
import json
import re
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup


def fetch_producthunt(limit: int = 10) -> List[Dict]:
    posts = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        response = requests.get("https://www.producthunt.com/", headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        # Yöntem 1: __NEXT_DATA__ JSON (Product Hunt Next.js kullanıyor)
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            posts = _parse_next_data(data, limit)
            if posts:
                return posts

        # Yöntem 2: HTML fallback
        soup = BeautifulSoup(html, "html.parser")
        posts = _parse_html(soup, limit)

    except Exception as e:
        print(f"  Product Hunt hatası: {e}")

    return posts[:limit]


def _parse_next_data(data: dict, limit: int) -> List[Dict]:
    """__NEXT_DATA__ içinden ürünleri çıkar."""
    posts = []
    try:
        # Yapı değişebilir; olası yolları dene
        apollo = data.get("props", {}).get("apolloState", {}) or data.get("props", {}).get("pageProps", {})

        # apolloState içinde Product node'larını ara
        if isinstance(apollo, dict):
            for key, val in apollo.items():
                if not isinstance(val, dict):
                    continue
                if val.get("__typename") == "Post" or "name" in val and "votesCount" in val:
                    name = val.get("name") or val.get("tagline") or ""
                    tagline = val.get("tagline") or val.get("description") or ""
                    votes = val.get("votesCount") or val.get("votes") or 0
                    slug = val.get("slug") or ""
                    url = f"https://www.producthunt.com/posts/{slug}" if slug else "https://www.producthunt.com/"
                    comments = val.get("commentsCount") or 0

                    if name:
                        posts.append({
                            "source": "product_hunt",
                            "title": f"{name} — {tagline}" if tagline else name,
                            "url": url,
                            "points": int(votes) if votes else 0,
                            "comments": int(comments) if comments else 0,
                            "fetched_at": datetime.now().isoformat(),
                        })
    except Exception:
        pass

    posts.sort(key=lambda x: x.get("points", 0), reverse=True)
    return posts[:limit]


def _parse_html(soup: BeautifulSoup, limit: int) -> List[Dict]:
    """Basit HTML fallback."""
    posts = []
    # Product Hunt sık değişir; genel link + oy pattern'i
    for item in soup.select("[data-test='post-item'], [class*='styles_item'], article")[:limit * 2]:
        try:
            link = item.select_one("a[href*='/posts/']")
            if not link:
                continue
            title = link.get_text().strip()
            href = link.get("href", "")
            url = href if href.startswith("http") else f"https://www.producthunt.com{href}"

            # Oy sayısı
            votes = 0
            vote_el = item.select_one("[class*='vote'], [data-test*='vote']")
            if vote_el:
                digits = "".join(filter(str.isdigit, vote_el.get_text()))
                votes = int(digits) if digits else 0

            if title and len(title) > 3:
                posts.append({
                    "source": "product_hunt",
                    "title": title,
                    "url": url,
                    "points": votes,
                    "comments": 0,
                    "fetched_at": datetime.now().isoformat(),
                })
        except Exception:
            continue

    posts.sort(key=lambda x: x.get("points", 0), reverse=True)
    return posts[:limit]


if __name__ == "__main__":
    import json
    results = fetch_producthunt(5)
    print(f"Bulunan: {len(results)}")
    print(json.dumps(results, indent=2, ensure_ascii=False))
