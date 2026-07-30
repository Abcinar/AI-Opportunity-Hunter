import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

def generate_id(source: str, title: str) -> str:
    """
    Source ve title değerlerinden MD5 hash üreterek benzersiz bir ID oluşturur.
    """
    s = str(source or "").strip()
    t = str(title or "").strip()
    raw_string = f"{s}_{t}"
    return hashlib.md5(raw_string.encode("utf-8")).hexdigest()

def normalize_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tekil bir sinyali/postu ortak veri modeline dönüştürür (normalize eder).
    """
    if not isinstance(post, dict):
        return {}

    source = str(post.get("source") or "").strip()
    if not source:
        source = "unknown"

    title = str(post.get("title") or "").strip()
    record_id = generate_id(source, title)

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

    return {
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

def remove_duplicates(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aynı ID'ye (source + title) sahip tekrarlı kayıtları temizler.
    """
    seen_ids = set()
    unique_signals: List[Dict[str, Any]] = []
    
    for post in signals:
        if not isinstance(post, dict):
            continue
            
        post_id = post.get("id")
        if not post_id:
            source = str(post.get("source") or "").strip() or "unknown"
            title = str(post.get("title") or "").strip()
            post_id = generate_id(source, title)
            
        if post_id in seen_ids:
            continue
            
        seen_ids.add(post_id)
        unique_signals.append(post)
        
    return unique_signals

def normalize_posts(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Tüm listeyi normalize eder ve duplicate kayıtları temizleyerek döner.
    """
    normalized_signals: List[Dict[str, Any]] = []
    
    for post in signals:
        if not isinstance(post, dict):
            continue
            
        normalized = normalize_post(post)
        if normalized:
            normalized_signals.append(normalized)
            
    return remove_duplicates(normalized_signals)

import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

def generate_id(source: str, title: str) -> str:
    """
    Source ve title değerlerinden MD5 hash üreterek benzersiz bir ID oluşturur.
    """
    s = str(source or "").strip()
    t = str(title or "").strip()
    raw_string = f"{s}_{t}"
    return hashlib.md5(raw_string.encode("utf-8")).hexdigest()

def normalize_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tekil bir sinyali/postu ortak veri modeline dönüştürür (normalize eder).
    """
    if not isinstance(post, dict):
        return {}

    source = str(post.get("source") or "").strip()
    if not source:
        source = "unknown"

    title = str(post.get("title") or "").strip()
    record_id = generate_id(source, title)

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

    return {
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

def remove_duplicates(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aynı ID'ye (source + title) sahip tekrarlı kayıtları temizler.
    """
    seen_ids = set()
    unique_signals: List[Dict[str, Any]] = []
    
    for post in signals:
        if not isinstance(post, dict):
            continue
            
        post_id = post.get("id")
        if not post_id:
            source = str(post.get("source") or "").strip() or "unknown"
            title = str(post.get("title") or "").strip()
            post_id = generate_id(source, title)
            
        if post_id in seen_ids:
            continue
            
        seen_ids.add(post_id)
        unique_signals.append(post)
        
    return unique_signals

def normalize_posts(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Tüm listeyi normalize eder ve duplicate kayıtları temizleyerek döner.
    """
    normalized_signals: List[Dict[str, Any]] = []
    
    for post in signals:
        if not isinstance(post, dict):
            continue
            
        normalized = normalize_post(post)
        if normalized:
            normalized_signals.append(normalized)
            
    return remove_duplicates(normalized_signals)
