"""
AI Opportunity Hunter
Opportunity Intelligence Engine V1

Görev:
- Bir sinyali analiz eder.
- Kanıt (evidence) üretir.
- Henüz puan vermez.
"""

from typing import Dict, List


# --------------------------------------------------
# Yardımcı Fonksiyonlar
# --------------------------------------------------

def _engagement_level(points: int) -> tuple[str, float]:
    """Etkileşim seviyesini belirler."""

    if points >= 1000:
        return "very_high", 0.95

    if points >= 500:
        return "high", 0.85

    if points >= 100:
        return "medium", 0.70

    if points >= 25:
        return "low", 0.55

    return "very_low", 0.35


def _momentum_level(source: str, points: int) -> tuple[str, float]:
    """Kaynağa göre momentum hesaplar."""

    source = source.lower()

    thresholds = {
        "github_trending": (1500, 500, 100),
        "hacker_news": (500, 200, 75),
        "reddit": (1000, 300, 75),
        "google_trends": (4000, 1000, 250),
        "product_hunt": (800, 250, 75),
        "betalist": (100, 40, 10),
        "lobsters": (150, 60, 20),
    }

    very_high, high, medium = thresholds.get(
        source,
        (1000, 300, 75)
    )

    if points >= very_high:
        return "very_high", 0.95

    if points >= high:
        return "high", 0.85

    if points >= medium:
        return "medium", 0.70

    return "low", 0.50


def _founder_fit(title: str) -> tuple[str, float]:
    """
    Solo founder açısından uygulanabilirlik.

    V1 tamamen kural tabanlı.
    """

    title = title.lower()

    good_keywords = [
        "ai",
        "automation",
        "tool",
        "api",
        "agent",
        "assistant",
        "dashboard",
        "analytics",
        "monitor",
        "workflow",
    ]

    score = sum(k in title for k in good_keywords)

    if score >= 3:
        return "high", 0.90

    if score >= 1:
        return "medium", 0.70

    return "low", 0.45


# --------------------------------------------------
# Evidence Builder
# --------------------------------------------------

def build_evidence(signal: Dict) -> List[Dict]:
    """
    Opportunity için kanıt üretir.
    """

    evidence = []

    title = signal.get("title", "")
    source = signal.get("source", "")
    points = int(signal.get("points", 0))

    # Engagement
    level, confidence = _engagement_level(points)

    evidence.append({
        "type": "engagement",
        "level": level,
        "confidence": confidence,
        "reason": f"{points} engagement detected"
    })

    # Momentum
    level, confidence = _momentum_level(source, points)

    evidence.append({
        "type": "momentum",
        "level": level,
        "confidence": confidence,
        "reason": f"Strong activity on {source}"
    })

    # Founder Fit
    level, confidence = _founder_fit(title)
# --------------------------------------------------
# Category Engine
# --------------------------------------------------

CATEGORY_RULES = {
    "AI": [
        "ai",
        "llm",
        "gpt",
        "agent",
        "copilot",
        "assistant",
        "rag",
        "embedding",
        "prompt",
        "model",
    ],

    "Developer Tools": [
        "api",
        "sdk",
        "framework",
        "library",
        "tool",
        "cli",
        "dashboard",
        "devops",
        "workflow",
    ],

    "Cyber Security": [
        "security",
        "auth",
        "oauth",
        "jwt",
        "password",
        "encryption",
        "vulnerability",
        "firewall",
    ],

    "Data": [
        "database",
        "sql",
        "postgres",
        "analytics",
        "warehouse",
        "etl",
        "pipeline",
    ],

    "Productivity": [
        "notes",
        "calendar",
        "task",
        "todo",
        "automation",
        "organizer",
    ]
}
def _detect_category(title: str) -> tuple[str, str]:
    """
    Başlığa göre kategori belirler.
    """

    text = title.lower()

    for category, keywords in CATEGORY_RULES.items():

        for keyword in keywords:

            if keyword in text:

                return category, keyword

    return "Other", ""
    TREND_LEVELS = {
    90: "exploding",
    75: "hot",
    55: "growing",
    0: "weak",
}


def _trend_strength(evidence: List[Dict]) -> str:
    """
    Evidence üzerinden trend gücü üretir.
    """

    score = 0

    for item in evidence:

        if item["type"] == "engagement":

            if item["level"] == "very_high":
                score += 45

            elif item["level"] == "high":
                score += 35

            elif item["level"] == "medium":
                score += 20

        elif item["type"] == "momentum":

            if item["level"] == "very_high":
                score += 45

            elif item["level"] == "high":
                score += 35

            elif item["level"] == "medium":
                score += 20

    for threshold, level in TREND_LEVELS.items():

        if score >= threshold:

            return level

    return "weak"
    evidence.append({
        "type": "founder_fit",
        "level": level,
        "confidence": confidence,
        "reason": "Estimated from title keywords"
    })

    return evidence


# --------------------------------------------------
# Intelligence Report
# --------------------------------------------------

def analyze_signal(signal: Dict) -> Dict:
    """
    Bir sinyalin ilk analizini döndürür.
    """

    evidence = build_evidence(signal)

    return {
        "id": signal.get("id"),
        "title": signal.get("title"),
        "source": signal.get("source"),
        "evidence": evidence,
    }
{
    "type":"momentum",
    "level":"high",
    "confidence":0.91,

    "importance":0.82,

    "reason":"Strong GitHub activity"
}

# --------------------------------------------------
# Toplu Analiz
# --------------------------------------------------

def analyze_signals(signals: List[Dict]) -> List[Dict]:
    """
    Tüm sinyalleri analiz eder.
    """

    return [analyze_signal(signal) for signal in signals]
