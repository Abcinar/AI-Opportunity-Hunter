"""
AI Opportunity Hunter - Main Entry Point
"""

import json
from datetime import datetime
from sources.hn_fetcher import fetch_hacker_news
from sources.reddit_fetcher import fetch_reddit_posts
from scoring import SignalInput, calculate_opportunity_score, result_to_dict
from rationale import generate_rationale


def fetch_all_signals(limit_per_source: int = 10) -> dict:
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
        "posts": all_posts[:20],
    }


def analyze_top_opportunities(posts: list, top_n: int = 3):
    """En yüksek sinyalli postları skorla + gerekçe üret."""
    print("\n" + "=" * 60)
    print(f"En İyi {top_n} Fırsat Analizi")
    print("=" * 60)

    results = []

    for i, post in enumerate(posts[:top_n], 1):
        title = post.get("title", "")
        source = post.get("source", "")
        points = post.get("points", 0) or post.get("score", 0)
        comments = post.get("comments", 0)

        # Basit skor (gerçek sinyal verisiyle daha sonra zenginleştirilecek)
        signals = SignalInput(
            hn_points=points if source == "hacker_news" else 0,
            hn_days_ago=2,
            reddit_upvotes=points if source == "reddit" else 0,
            i_would_pay_count=3,
            time_waste_mentions=2,
            direct_competitors=2,
            big_player_exists=False,
            tech_complexity="medium",
            required_integrations=1,
            pricing_discussed=True,
            existing_paid_alternatives=True,
        )

        score_result = calculate_opportunity_score(signals)
        rationale = generate_rationale(
            title=title,
            source=source,
            points=points,
            comments=comments,
            score_breakdown=result_to_dict(score_result)["breakdown"],
            language="tr",
        )

        print(f"\n--- Fırsat #{i} ---")
        print(f"Başlık     : {title[:80]}...")
        print(f"Kaynak     : {source} | Puan: {points} | Yorum: {comments}")
        print(f"Skor       : {score_result.total_score}/100 ({score_result.label})")
        print(f"Gerekçe    : {rationale}")

        results.append({
            "title": title,
            "source": source,
            "points": points,
            "comments": comments,
            "score": result_to_dict(score_result),
            "rationale": rationale,
        })

    return results


def save_signals(data: dict, filename: str = "daily_signals.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  Veriler kaydedildi → {filename}")


if __name__ == "__main__":
    signals = fetch_all_signals(limit_per_source=8)
    save_signals(signals)

    # En iyi fırsatları analiz et + gerekçe üret
    analyze_top_opportunities(signals["posts"], top_n=3)

    print("\n" + "=" * 60)
    print("Tamamlandı.")
    print("=" * 60)
