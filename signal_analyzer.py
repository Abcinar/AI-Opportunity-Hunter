"""
AI Opportunity Hunter - Signal Analyzer
GitHub Trending için özel skor mantığı dahil.
"""

import re
import math
from typing import Dict, Any
from scoring import SignalInput


PAIN_KEYWORDS = [
    "problem", "hate", "frustrated", "annoying", "expensive", "slow",
    "broken", "sucks", "pain", "struggle", "difficult", "hard to",
    "wish there was", "looking for", "need a", "alternative to",
    "sorun", "pahali", "yavas", "kotu",
]

COMPETITION_KEYWORDS = [
    "alternative", "vs", "versus", "better than", "instead of",
    "open source", "self-hosted", "competitor", "compared to",
]

FEASIBILITY_POSITIVE = [
    "simple", "easy", "no-code", "low-code", "api", "script",
    "weekend project", "side project", "mvp", "lightweight",
    "basit", "kolay", "i built", "i made", "i launched",
    "cli", "tool", "extension", "plugin", "boilerplate",
]

FEASIBILITY_NEGATIVE = [
    "enterprise", "complex", "infrastructure", "hardware",
    "regulated", "compliance", "deep learning", "requires team",
    "distributed", "kubernetes", "cluster", "platform",
]

MONETIZATION_KEYWORDS = [
    "paid", "pricing", "subscription", "revenue", "monetize",
    "saas", "price", "billing", "pay", "customer", "business model",
]

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
    r"mvp",
    r"side project",
    r"weekend project",
    r"looking for",
    r"need a tool",
    r"is there a",
    r"how do you",
    r"what do you use",
    r"cli",
    r"\btool\b",
    r"boilerplate",
]

NOISE_PATTERNS = [
    r"raises \$?\d",
    r"acquires?",
    r"announces?",
    r"stock",
    r"earnings",
    r"layoffs?",
    r"ceo of",
    r"interview with",
    r"passes away",
    r"what are you working on",
    r"who is hiring",
    r"who wants to be hired",
]

# GitHub'a özel olumlu sinyaller
GITHUB_TOOL_KEYWORDS = [
    "cli", "tool", "sdk", "library", "framework", "boilerplate",
    "template", "starter", "extension", "plugin", "api",
    "alternative", "wrapper", "helper", "utility", "dashboard",
    "monitor", "tracker", "generator", "converter",
]


def _count_keywords(text: str, keywords: list) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def is_likely_opportunity(title: str) -> bool:
    t = title.lower()
    for pat in NOISE_PATTERNS:
        if re.search(pat, t):
            return False
    for pat in OPPORTUNITY_PATTERNS:
        if re.search(pat, t):
            return True
    return False


def _github_star_score(stars: int) -> int:
    """
    Günlük star sayısını 0-100 arasına log ölçekle map et.
    0-50 → 20-40 | 50-200 → 40-70 | 200-500 → 70-90 | 500+ → 90-100
    """
    if stars <= 0:
        return 10
    # log ölçek: 10 star ≈ 30, 100 ≈ 55, 500 ≈ 75, 2000 ≈ 90
    score = 15 + (math.log10(stars + 1) * 28)
    return int(min(max(score, 10), 100))


def _analyze_github(post: Dict[str, Any]) -> SignalInput:
    """GitHub Trending post'ları için özel analiz."""
    title = post.get("title", "")
    stars = post.get("points", 0) or 0
    text = title.lower()

    # Momentum: star (log) + tool keyword boost + freshness (daily=yüksek)
    star_score = _github_star_score(stars)
    tool_hits = _count_keywords(text, GITHUB_TOOL_KEYWORDS)
    tool_boost = min(tool_hits * 12, 40)

    # Momentum'u SignalInput alanlarıyla taşıyoruz:
    # hn_points yerine star_score'u ölçekleyip hn_points'e yazıyoruz
    # freshness için hn_days_ago=1 (daily trending)
    hn_points = int(star_score * 3.5)          # scoring formülünde /4 → ~star_score
    hn_days_ago = 1                            # daily → yüksek freshness
    reddit_upvotes = tool_boost * 2            # keyword boost

    # Pain: GitHub başlıklarında nadir, tool/alternative varsa hafif artir
    pain = 0
    if "alternative" in text or "replace" in text or "instead" in text:
        pain = 3
    if any(w in text for w in ["simple", "easy", "lightweight"]):
        pain += 1

    # Competition
    comp_hits = _count_keywords(text, COMPETITION_KEYWORDS)
    if comp_hits >= 1 or "alternative" in text:
        direct_competitors = 1
    else:
        direct_competitors = 3

    big_player = any(
        x in text
        for x in ["google", "microsoft", "amazon", "meta", "openai", "apple", "facebook"]
    )

    # Solo feasibility
    pos = _count_keywords(text, FEASIBILITY_POSITIVE)
    neg = _count_keywords(text, FEASIBILITY_NEGATIVE)
    if pos > neg and pos >= 1:
        tech_complexity = "low"
        integrations = 1
    elif neg >= 2 or any(w in text for w in ["platform", "infrastructure", "distributed"]):
        tech_complexity = "high"
        integrations = 3
    else:
        tech_complexity = "medium"
        integrations = 2

    # Monetization: GitHub'da zayıf sinyal
    mon_hits = _count_keywords(text, MONETIZATION_KEYWORDS)
    pricing_discussed = mon_hits >= 1
    existing_paid = mon_hits >= 2 or "saas" in text

    return SignalInput(
        hn_points=hn_points,
        hn_days_ago=hn_days_ago,
        reddit_upvotes=reddit_upvotes,
        i_would_pay_count=pain,
        time_waste_mentions=min(pain, 3),
        direct_competitors=direct_competitors,
        big_player_exists=big_player,
        tech_complexity=tech_complexity,
        required_integrations=integrations,
        pricing_discussed=pricing_discussed,
        existing_paid_alternatives=existing_paid,
    )


def analyze_post(post: Dict[str, Any]) -> SignalInput:
    """
    Kaynağa göre uygun analiz yolunu seçer.
    """
    source = post.get("source", "")

    # GitHub için özel yol
    if source == "github_trending":
        return _analyze_github(post)

    # --- HN / Lobsters / Reddit (mevcut mantık) ---
    title = post.get("title", "")
    points = post.get("points", 0) or post.get("score", 0)
    comments = post.get("comments", 0)
    text = title
    likely = is_likely_opportunity(title)

    if source in ("hacker_news", "lobsters"):
        hn_points = points
        reddit_upvotes = 0
        hn_days_ago = 1 if points > 200 else 3
    else:
        hn_points = 0
        reddit_upvotes = points
        hn_days_ago = 5

    pain_hits = _count_keywords(text, PAIN_KEYWORDS)
    i_would_pay = min(pain_hits + (1 if comments > 50 else 0), 8)
    time_waste = min(pain_hits, 5)
    if not likely:
        i_would_pay = max(0, i_would_pay - 2)
        time_waste = 0

    comp_hits = _count_keywords(text, COMPETITION_KEYWORDS)
    if comp_hits >= 2:
        direct_competitors = 1
    elif comp_hits == 1:
        direct_competitors = 2
    else:
        direct_competitors = 3

    big_player = any(
        x in text.lower()
        for x in ["google", "microsoft", "amazon", "meta", "openai", "apple"]
    )

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

    mon_hits = _count_keywords(text, MONETIZATION_KEYWORDS)
    pricing_discussed = mon_hits >= 1 if likely else False
    existing_paid = (mon_hits >= 2 or "saas" in text.lower()) if likely else False

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
    tests = [
        {
            "title": "koala73/worldmonitor — Real-time global intelligence dashboard",
            "source": "github_trending",
            "points": 3175,
            "comments": 0,
        },
        {
            "title": "someuser/simple-cli-tool — A lightweight CLI alternative to X",
            "source": "github_trending",
            "points": 120,
            "comments": 0,
        },
        {
            "title": "Show HN: I built a simple API alternative to expensive support tools",
            "source": "hacker_news",
            "points": 320,
            "comments": 95,
        },
    ]
    for t in tests:
        s = analyze_post(t)
        print(f"\n{t['title'][:55]}")
        print(f"  source={t['source']} stars/points={t['points']}")
        print(f"  hn_points={s.hn_points} days={s.hn_days_ago} reddit={s.reddit_upvotes}")
        print(f"  pain={s.i_would_pay_count} solo={s.tech_complexity} comps={s.direct_competitors}")
