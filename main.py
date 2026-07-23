"""
AI Opportunity Hunter - Main Entry Point
-----------------------------------------
Sinyal toplama + Opportunity Score hesaplama
"""

import json
from datetime import datetime
from sources.hn_fetcher import fetch_hacker_news
from sources.reddit_fetcher import fetch_reddit_posts
from scoring import SignalInput, calculate_opportunity_score, result_to_dict


def fetch_all_signals(limit_per_source: int = 12) -> dict:
    print("=" * 60)
    print("AI Opportunity Hunter - Sinyal Toplama Başladı")
    print("=" * 60)

    hn_posts = fetch_hacker_news(limit=limit_per_source)
    print(f"  Hacker News  → {len(hn_posts)} sinyal alındı")

    reddit_posts = fetch_reddit_posts(limit=limit_per_source)
    print(f"  Reddit       → {len(reddit_posts)} sinyal alındı")

    all_posts = hn_posts + reddit_posts
    all_posts.sort(
        key=lambda x: (x.get("points", 0) or x.get("score", 0), x.get("comments", 0)),
        reverse=True,
    )

    return {
        "fetched_at": datetime.now().isoformat(),
        "total_signals": len(all_posts),
        "sources": {
            "hacker_news": len(hn_posts),
            "reddit": len(reddit_posts),
        },
        "posts": all_posts[:30],
    }


def demo_scoring():
    print("\n" + "=" * 60)
    print("Opportunity Score - Demo")
    print("=" * 60)

    example = SignalInput(
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

    result = calculate_opportunity_score(example)

    print(f"\n  Toplam Skor           : {result.total_score}/100")
    print(f"  Etiket                : {result.label}")
    print(f"\n  Momentum              : {result.breakdown.momentum}")
    print(f"  Pain Clarity          : {result.breakdown.pain_clarity}")
    print(f"  Competition Gap       : {result.breakdown.competition_gap}")
    print(f"  Solo Feasibility      : {result.breakdown.solo_feasibility}")
    print(f"  Monetization Clarity  : {result.breakdown.monetization_clarity}")

    return result_to_dict(result)


def save_signals(data: dict, filename: str = "daily_signals.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  Veriler kaydedildi → {filename}")


if __name__ == "__main__":
    signals = fetch_all_signals(limit_per_source=10)
    save_signals(signals)
    demo_scoring()
    print("\n" + "=" * 60)
    print("Tamamlandı.")
    print("=" * 60)
