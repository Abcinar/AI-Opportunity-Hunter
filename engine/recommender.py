"""
Recommendation Engine
"""

from typing import Dict


def recommend(score: Dict) -> Dict:

    overall = score["overall_score"]

    if overall >= 85:
        decision = "BUILD"

    elif overall >= 70:
        decision = "INVESTIGATE"

    elif overall >= 50:
        decision = "WATCH"

    else:
        decision = "SKIP"

    return {

    "decision":decision,

    "overall_score":overall,

    "confidence":score["confidence"],

    "emoji":emoji,

    "color":color

}
