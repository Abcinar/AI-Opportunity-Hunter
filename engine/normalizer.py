"""
AI Opportunity Hunter
Signal Normalizer

Görevleri:
- Tüm kaynakları ortak veri modeline dönüştürmek
- Eksik alanları tamamlamak
- Basit duplicate temizliği yapmak
"""

from __future__ import annotations

from datetime import datetime
import hashlib
from typing import Dict, List


def generate_id(title: str, source: str) -> str:
    """Başlık + kaynak kullanarak benzersiz ID üretir."""
    key = f"{source}:{title}".lower().strip()
    return hashlib.md5(key.encode("utf-8")).hexdigest()[:12]


def normalize_post(post: Dict) -> Dict:
    """Tek bir kaynağı standart Opportunity Signal formatına çevirir."""

    title = str(post.get("title", "")).strip()

    source = str(post.get("source", "unknown")).strip()

    url = str(post.get("url", "")).strip()

    points = int(post.get("points") or post.get("score") or 0)

    comments = int(post.get("comments") or 0)

    fetched = post.get("fetched_at")

    if not fetched:
        fetched = datetime.utcnow().isoformat()

    return {
        "id": generate_id(title, source),

        "title": title,

        "summary": "",

        "source": source,

        "url": url,

        "engagement": points,

        "points": points,

        "comments": comments,

        "category": "unknown",

        "tags": [],

        "language": "unknown",

        "collected_at": fetched,
    }


def remove_duplicates(posts: List[Dict]) -> List[Dict]:
    """
    Aynı başlığa sahip kayıtları temizler.

    İlk sürümde sadece title bazlı duplicate kontrolü yapıyoruz.
    """

    seen = set()

    cleaned = []

    for post in posts:

        key = post["title"].lower().strip()

        if key in seen:
            continue

        seen.add(key)

        cleaned.append(post)

    return cleaned


def normalize_posts(posts: List[Dict]) -> List[Dict]:
    """
    Tüm postları normalize eder.
    """

    normalized = []

    for post in posts:
        normalized.append(normalize_post(post))

    normalized = remove_duplicates(normalized)

    return normalized
