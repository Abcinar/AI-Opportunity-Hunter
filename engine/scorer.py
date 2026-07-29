"""
engine/scorer.py
AI Opportunity Hunter
Scoring Engine V1

Evidence -> Opportunity Score
"""

from typing import Dict, List, Any, Union


LEVEL_SCORE = {
    "very_high": 100,
    "high": 80,
    "medium": 60,
    "low": 35,
    "very_low": 15,
}


WEIGHTS = {
    "engagement": 0.40,
    "momentum": 0.35,
    "founder_fit": 0.25
}


def score_from_level(level: str) -> int:
    return LEVEL_SCORE.get(level, 0)


def calculate_score(evidence: Union[List[Dict], Dict[str, Any]]) -> Dict:
    """
    Evidence verisinden Opportunity Score üretir.
    Hem eski V1 listesini hem de yeni V2 sözlük yapısını güvenli okur.
    """

    weighted_total = 0.0
    confidence_sum = 0.0
    breakdown = {}
    
    # Eğer yeni V2 mimarisinden sözlük geldiyse listeye sar veya boş liste yap
    if isinstance(evidence, dict):
        evidence_list = []
        # V2 yapısına basit bir adaptasyon (Scorer V2 yazılana kadar çökmemesi için)
        if evidence.get("has_clear_pain"):
            evidence_list.append({"type": "founder_fit", "level": "high", "confidence": 80.0})
    elif isinstance(evidence, list):
        evidence_list = evidence
    else:
        evidence_list = []

    for item in evidence_list:
        if not isinstance(item, dict):
            continue

        ev_type = item.get("type", "unknown")
        level = item.get("level", "low")
        confidence = float(item.get("confidence", 0.0))

        score = score_from_level(level)

        breakdown[ev_type] = {
            "level": level,
            "score": score,
            "confidence": confidence,
        }

        weight = WEIGHTS.get(ev_type, 0.0)
        weighted_total += score * weight
        confidence_sum += confidence

    item_count = max(len(evidence_list), 1)
    
    confidence_final = round((confidence_sum / item_count) * 100, 1)
    if confidence_sum == 0 and isinstance(evidence, dict) and evidence:
        # V2 formatından geldiyse default bir confidence değeri dön
        confidence_final = 50.0

    overall = round(weighted_total)

    return {
        "overall_score": overall,
        "confidence": confidence_final,
        "breakdown": breakdown,
    }
