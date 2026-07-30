import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List


class Normalizer:
    def __init__(self) -> None:
        pass

    def normalize(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized_signals: List[Dict[str, Any]] = []
        seen_ids = set()

        for post in signals:
            if not isinstance(post, dict):
                continue

            source = str(post.get("source") or "").strip()
            if not source:
                source = "unknown"

            title = str(post.get("title") or "").strip()

            raw_id_string = f"{source}_{title}"
            record_id = hashlib.md5(raw_id_string.encode("utf-8")).hexdigest()

            if record_id in seen_ids:
                continue
            seen_ids.add(record_id)

            summary = str(
                post.get("summary") or 
                post.get("content") or 
                post.get("description") or 
                ""
            ).strip()
            
            content = summary

            raw_points = post.get("points")
            if raw_points is None:
                raw_points = post.get("score")
            if raw_points is None:
                raw_points = post.get("upvotes")

            try:
                points = int(raw_points) if raw_points is not None else 0
            except (ValueError, TypeError):
                points = 0

            upvotes = points
            engagement = points

            raw_comments = post.get("comments")
            if raw_comments is None:
                raw_comments = post.get("num_comments")

            try:
                comments = int(raw_comments) if raw_comments is not None else 0
            except (ValueError, TypeError):
                comments = 0

            tags = post.get("tags")
            if not isinstance(tags, list):
                tags = []

            category = str(post.get("category") or "unknown").strip()
            language = str(post.get("language") or "unknown").strip()
            url = str(post.get("url") or "").strip()

            collected_at = str(
                post.get("fetched_at") or 
                post.get("collected_at") or 
                datetime.now(timezone.utc).isoformat()
            ).strip()

            normalized_signal = {
                "id": record_id,
                "title": title,
                "summary": summary,
                "content": content,
                "source": source,
                "url": url,
                "engagement": engagement,
                "points": points,
                "upvotes": upvotes,
                "comments": comments,
                "category": category,
                "tags": tags,
                "language": language,
                "collected_at": collected_at
            }

            normalized_signals.append(normalized_signal)

        return normalized_signals
