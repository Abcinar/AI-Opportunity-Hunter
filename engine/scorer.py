"""
AI Opportunity Hunter
Scoring Engine V1

Evidence -> Opportunity Score
"""

from typing import Dict, List


LEVEL_SCORE = {
    "very_high": 100,
    "high": 80,
    "medium": 60,
    "low": 35,
    "very_low": 15,
}


WEIGHTS = {
    "engagement": 0.35,
    "momentum": 0.30,
    "founder_fit": 0.20,
    "confidence": 0.15,
}


def score_from_level(level: str) -> int:
    return LEVEL_SCORE.get(level, 0)


def calculate_score(evidence: List[Dict]) -> Dict:
    """
    Evidence listesinden Opportunity Score üretir.
    """

    weighted_total = 0.0
    confidence_sum = 0.0

    breakdown = {}

    for item in evidence:

        ev_type = item["type"]

        level = item["level"]

        confidence = float(item["confidence"])

        score = score_from_level(level)

        breakdown[ev_type] = {
            "level": level,
            "score": score,
            "confidence": confidence,
        }

        weight = WEIGHTS.get(ev_type, 0)

        weighted_total += score * weight

        confidence_sum += confidence

    confidence = round(
        (confidence_sum / max(len(evidence), 1)) * 100,
        1,
    )

    overall = round(weighted_total)

    return {
        "overall_score": overall,
        "confidence": confidence,
        "breakdown": breakdown,
    }
