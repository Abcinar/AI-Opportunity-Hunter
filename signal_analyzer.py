# Fırsat sinyali veren kalıplar
OPPORTUNITY_PATTERNS = [
    r"show hn",
    r"ask hn",
    r"i built",
    r"i made",
    r"i launched",
    r"alternative to",
    r"open[- ]source",
    r"self[- ]hosted",
    r"saas",
    r"for freelancers",
    r"for indie",
    r"for solo",
    r"for small (business|teams|shops)",
    r"mvp",
    r"side project",
    r"weekend project",
    r"looking for",
    r"need a tool",
    r"is there a",
    r"how do you",
    r"what do you use",
]

# Elemek istediğimiz haber/tartışma kalıpları
NOISE_PATTERNS = [
    r"raises \$?\d",
    r"acquires?",
    r"announces?",
    r"launches? ipo",
    r"stock",
    r"earnings",
    r"layoffs?",
    r"ceo of",
    r"interview with",
    r"passes away",
    r"dies at",
]


def is_likely_opportunity(title: str) -> bool:
    """Başlık fırsat sinyali taşıyor mu?"""
    t = title.lower()

    # Önce gürültü mü bak
    for pat in NOISE_PATTERNS:
        if re.search(pat, t):
            return False

    # Fırsat kalıbı var mı
    for pat in OPPORTUNITY_PATTERNS:
        if re.search(pat, t):
            return True

    # Hiçbiri yoksa: orta seviye — yüksek etkileşimliyse geçir
    return False
"""
AI Opportunity Hunter - Signal Analyzer
---------------------------------------
Ham post verisinden Opportunity Score için
gerçekçi SignalInput üretir.
"""

import re
from typing import Dict, Any
from scoring import SignalInput


# Anahtar kelime listeleri
PAIN_KEYWORDS = [
    "problem", "hate", "frustrated", "annoying", "expensive", "slow",
    "broken", "sucks", "pain", "struggle", "difficult", "hard to",
    "wish there was", "looking for", "need a", "alternative to",
    "sorun", "pahalı", "yavaş", "kötü", "çalışmıyor",
]

COMPETITION_KEYWORDS = [
    "alternative", "vs", "versus", "better than", "instead of",
    "open source", "self-hosted", "competitor", "compared to",
]

FEASIBILITY_POSITIVE = [
    "simple", "easy", "no-code", "low-code", "api", "script",
    "weekend project", "side project", "mvp", "lightweight",
    "basit", "kolay",
]

FEASIBILITY_NEGATIVE = [
    "enterprise", "complex", "infrastructure", "hardware",
    "regulated", "compliance", "machine learning research",
    "deep learning", "requires team",
]

MONETIZATION_KEYWORDS = [
    "paid", "pricing", "subscription", "revenue", "monetize",
    "saas", "price", "billing", "pay", "customer", "business model",
    "ücretli", "fiyat", "abonelik",
]


def _count_keywords(text: str, keywords: list) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def analyze_post(post: Dict[str, Any]) -> SignalInput:
    """
    Tek bir post'tan SignalInput üretir.
    """
    title = post.get("title", "")
    source = post.get("source", "")
    points = post.get("points", 0) or post.get("score", 0)
    comments = post.get("comments", 0)
    text = title  # İleride body/snippet eklenebilir

    # --- Momentum ---
    # points + comments + kaynak ağırlığı
    if source == "hacker_news":
        hn_points = points
        reddit_upvotes = 0
        # Tazelik: HN front page'de olduğu için yakın kabul ediyoruz
        hn_days_ago = 1 if points > 200 else 3
    else:
        hn_points = 0
        reddit_upvotes = points
        hn_days_ago = 5

    # --- Pain Clarity ---
    pain_hits = _count_keywords(text, PAIN_KEYWORDS)
    # Yorum sayısı da acı göstergesi olabilir
    i_would_pay = min(pain_hits + (1 if comments > 50 else 0), 8)
    time_waste = min(pain_hits, 5)

    # --- Competition Gap ---
    comp_hits = _count_keywords(text, COMPETITION_KEYWORDS)
    if comp_hits >= 2:
        direct_competitors = 1
    elif comp_hits == 1:
        direct_competitors = 2
    else:
        direct_competitors = 3  # bilmiyoruz, orta varsay

    big_player = any(x in text.lower() for x in ["google", "microsoft", "amazon", "meta", "openai", "apple"])

    # --- Solo Feasibility ---
    pos = _count_keywords(text, FEASIBILITY_POSITIVE)
    neg = _count_keywords(text, FEASIBILITY_NEGATIVE)

    if pos > neg and pos >= 1:
        tech_complexity = "low"
        integrations = 1
    elif neg > pos:
        tech_complexity = "high"
        integrations = 3
    else:
        tech_complexity = "medium"
        integrations = 2

    # --- Monetization ---
    mon_hits = _count_keywords(text, MONETIZATION_KEYWORDS)
    pricing_discussed = mon_hits >= 1
    existing_paid = mon_hits >= 2 or "saas" in text.lower()

    return SignalInput(
        hn_points=hn_points,
        hn_days_ago=hn_days_ago,
        reddit_upvotes=reddit_upvotes,
        i_would_pay_count=i_would_pay,
        time_waste_mentions=time_waste,
        direct_competitors=direct_competitors,
        big_player_exists=big_player,
        tech_complexity=tech_complexity,
        required_integrations=integrations,
        pricing_discussed=pricing_discussed,
        existing_paid_alternatives=existing_paid,
    )


if __name__ == "__main__":
    # Test
    test_post = {
        "title": "I built a simple API alternative to expensive customer support tools",
        "source": "hacker_news",
        "points": 320,
        "comments": 95,
    }
    signals = analyze_post(test_post)
    print(signals)
