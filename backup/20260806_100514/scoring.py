"""
AI Opportunity Hunter - Opportunity Score Engine
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class SignalInput:
    hn_points: int = 0
    hn_days_ago: int = 30
    reddit_upvotes: int = 0
    i_would_pay_count: int = 0
    time_waste_mentions: int = 0
    direct_competitors: int = 0
    big_player_exists: bool = False
    tech_complexity: str = "medium"
    required_integrations: int = 0
    pricing_discussed: bool = False
    existing_paid_alternatives: bool = False


@dataclass
class ScoreBreakdown:
    momentum: int
    pain_clarity: int
    competition_gap: int
    solo_feasibility: int
    monetization_clarity: int


@dataclass
class OpportunityScoreResult:
    total_score: int
    breakdown: ScoreBreakdown
    weights: Dict[str, float]
    label: str
    rationale_key: str


WEIGHTS = {
    "momentum": 0.25,
    "pain_clarity": 0.20,
    "competition_gap": 0.20,
    "solo_feasibility": 0.20,
    "monetization_clarity": 0.15,
}


def _calc_momentum(signals: SignalInput) -> int:
    hn_score = min(signals.hn_points / 4.0, 100)
    if signals.hn_days_ago <= 3:
        freshness = 100
    elif signals.hn_days_ago <= 7:
        freshness = 85
    elif signals.hn_days_ago <= 14:
        freshness = 60
    else:
        freshness = 30
    reddit_score = min(signals.reddit_upvotes / 2.0, 100)
    momentum = (hn_score * 0.50) + (freshness * 0.30) + (reddit_score * 0.20)
    return int(round(min(momentum, 100)))


def _calc_pain_clarity(signals: SignalInput) -> int:
    score = 0
    score += signals.i_would_pay_count * 12
    score += signals.time_waste_mentions * 10
    return int(round(min(score, 100)))


def _calc_competition_gap(signals: SignalInput) -> int:
    count = signals.direct_competitors
    if count == 0:
        gap = 95
    elif count <= 2:
        gap = 80
    elif count <= 5:
        gap = 55
    else:
        gap = 30
    if signals.big_player_exists:
        gap = max(gap - 20, 10)
    return int(gap)


def _calc_solo_feasibility(signals: SignalInput) -> int:
    complexity_map = {"low": 90, "medium": 70, "high": 40}
    score = complexity_map.get(signals.tech_complexity, 50)
    score -= signals.required_integrations * 5
    return int(max(min(score, 100), 10))


def _calc_monetization_clarity(signals: SignalInput) -> int:
    score = 40
    if signals.pricing_discussed:
        score += 30
    if signals.existing_paid_alternatives:
        score += 25
    return int(min(score, 100))


def calculate_opportunity_score(signals: SignalInput) -> OpportunityScoreResult:
    breakdown = ScoreBreakdown(
        momentum=_calc_momentum(signals),
        pain_clarity=_calc_pain_clarity(signals),
        competition_gap=_calc_competition_gap(signals),
        solo_feasibility=_calc_solo_feasibility(signals),
        monetization_clarity=_calc_monetization_clarity(signals),
    )
    total = (
        breakdown.momentum * WEIGHTS["momentum"] +
        breakdown.pain_clarity * WEIGHTS["pain_clarity"] +
        breakdown.competition_gap * WEIGHTS["competition_gap"] +
        breakdown.solo_feasibility * WEIGHTS["solo_feasibility"] +
        breakdown.monetization_clarity * WEIGHTS["monetization_clarity"]
    )
    final_score = int(round(total))
    if final_score >= 80:
        label = "very_strong"
    elif final_score >= 65:
        label = "good"
    elif final_score >= 50:
        label = "medium"
    else:
        label = "weak"
    return OpportunityScoreResult(
        total_score=final_score,
        breakdown=breakdown,
        weights=WEIGHTS,
        label=label,
        rationale_key=label,
    )


def score_from_dict(data: Dict[str, Any]) -> OpportunityScoreResult:
    signals = SignalInput(**data)
    return calculate_opportunity_score(signals)


def result_to_dict(result: OpportunityScoreResult) -> Dict[str, Any]:
    return {
        "total_score": result.total_score,
        "label": result.label,
        "breakdown": asdict(result.breakdown),
        "weights": result.weights,
    }


if __name__ == "__main__":
    example_signals = SignalInput(
        hn_points=312,
        hn_days_ago=4,
        reddit_upvotes=140,
        i_would_pay_count=6,
        time_waste_mentions=4,
        direct_competitors=2,
        big_player_exists=False,
        tech_complexity="medium",
        required_integrations=2,
        pricing_discussed=True,
        existing_paid_alternatives=True,
    )
    result = calculate_opportunity_score(example_signals)
    print("=" * 50)
    print("AI Opportunity Hunter - Score Engine")
    print("=" * 50)
    print(f"\nToplam Skor      : {result.total_score}/100")
    print(f"Etiket           : {result.label}")
    print("\nBileşenler:")
    print(f"  Momentum              : {result.breakdown.momentum}")
    print(f"  Pain Clarity          : {result.breakdown.pain_clarity}")
    print(f"  Competition Gap       : {result.breakdown.competition_gap}")
    print(f"  Solo Feasibility      : {result.breakdown.solo_feasibility}")
    print(f"  Monetization Clarity  : {result.breakdown.monetization_clarity}")
