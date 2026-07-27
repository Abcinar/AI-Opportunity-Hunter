"""
Recommendation Engine
"""

from typing import Dict


def recommend(score: Dict) -> Dict:

    overall = score["overall_score"]

    if overall >= 85:
        decision = "BUILD"
        emoji = "🚀"
        color = "green"

    elif overall >= 70:
        decision = "INVESTIGATE"
        emoji = "🔍"
        color = "blue"

    elif overall >= 50:
        decision = "WATCH"
        emoji = "👀"
        color = "orange"

    else:
        decision = "SKIP"
        emoji = "❌"
        color = "red"

    return {
        "decision": decision,
        "overall_score": overall,
        "confidence": score["confidence"],
        "emoji": emoji,
        "color": color,
    }
