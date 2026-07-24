"""
BetaList Fetcher
Yeni startup / ürün lansmanlarını çeker.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict


def fetch_betalist(limit: int = 10) -> List[Dict]:
    posts = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get("https://betalist.com/", headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # BetaList kart yapısı
        cards = soup.select(".startupCard, .startup, article, .card")
        if not cards:
            # Alternatif selector
            cards = soup.select("a[href*='/startups/']")

        seen = set()
        for card in cards:
            if len(posts) >= limit:
                break
            try:
                # Baslik
                title_el = card.select_one("h2, h3, .startupCard__title, .title")
                if title_el:
                    title = title_el.get_text().strip()
                    link_el = title_el.find("a") if title_el.name != "a" else title_el
                else:
                    link_el = card if card.name == "a" else card.select_one("a")
                    title = link_el.get_text().strip() if link_el else ""

                if not title or len(title) < 3:
                    continue
                if title.lower() in seen:
                    continue
                seen.add(title.lower())

                # URL
                href = ""
                if link_el:
                    href = link_el.get("href", "")
                elif card.name == "a":
                    href = card.get("href", "")
                url = href if href.startswith("http") else f"https://betalist.com{href}"

                # Aciklama
                desc_el = card.select_one("p, .startupCard__description, .description, .tagline")
                desc = desc_el.get_text().strip() if desc_el else ""

                full_title = f"{title} — {desc}" if desc else title

                posts.append({
                    "source": "betalist",
                    "title": full_title[:120],
                    "url": url,
                    "points": 50,  # BetaList'te oy yok, sabit orta deger
                    "comments": 0,
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception:
                continue

    except Exception as e:
        print(f"  BetaList hatasi: {e}")

    return posts[:limit]


if __name__ == "__main__":
    import json
    results = fetch_betalist(5)
    print(f"Bulunan: {len(results)}")
    print(json.dumps(results, indent=2, ensure_ascii=False))
