"""
AI Opportunity Hunter - Main Entry Point
"""

import json
from datetime import datetime
from sources.hn_fetcher import fetch_hacker_news
from sources.reddit_fetcher import fetch_reddit_posts
from sources.lobsters_fetcher import fetch_lobsters
from sources.github_fetcher import fetch_github_trending
from scoring import calculate_opportunity_score, result_to_dict
from rationale import generate_rationale
from monitor import OpportunityMonitor
from signal_analyzer import analyze_post, is_likely_opportunity
from sources.producthunt_fetcher import fetch_producthunt


def print_header(title: str):
    print("\n" + "═" * 64)
    print(f"  {title}")
    print("═" * 64)


def print_opportunity(index: int, post: dict, score_result, rationale: str):
    title = post.get("title", "")[:70]
    source = post.get("source", "")
    points = post.get("points", 0) or post.get("score", 0)
    comments = post.get("comments", 0)
    total = score_result.total_score
    label = score_result.label

    label_tr = {
        "very_strong": "Çok Güçlü",
        "good": "İyi",
        "medium": "Orta",
        "weak": "Zayıf",
    }.get(label, label)

    print(f"""
┌─ Fırsat #{index} ─────────────────────────────────────────────
│  {title}
│
│  Kaynak   : {source.upper()}
│  Etkileşim: {points} puan  ·  {comments} yorum
│  Skor     : {total}/100  ({label_tr})
│
│  Momentum {score_result.breakdown.momentum:>3}  │  Pain {score_result.breakdown.pain_clarity:>3}  │  Gap {score_result.breakdown.competition_gap:>3}
│  Solo     {score_result.breakdown.solo_feasibility:>3}  │  Money {score_result.breakdown.monetization_clarity:>3}
│
│  Gerekçe  :
│  {rationale}
└──────────────────────────────────────────────────────────────""")


def fetch_all_signals(limit_per_source: int = 10) -> dict:
    print_header("Sinyal Toplama")

    hn_posts = fetch_hacker_news(limit=limit_per_source)
    print(f"  ✓ Hacker News     → {len(hn_posts)} sinyal")

    lobsters_posts = fetch_lobsters(limit=limit_per_source)
    print(f"  ✓ Lobsters        → {len(lobsters_posts)} sinyal")

    github_posts = fetch_github_trending(limit=limit_per_source)
    print(f"  ✓ GitHub Trending → {len(github_posts)} sinyal")

    reddit_posts = fetch_reddit_posts(limit=limit_per_source)
    print(f"  ✓ Reddit          → {len(reddit_posts)} sinyal")

    ph_posts = fetch_producthunt(limit=limit_per_source)
    print(f"  ✓ Product Hunt    → {len(ph_posts)} sinyal")

    all_posts = hn_posts + lobsters_posts + github_posts + ph_posts + reddit_posts
    (
        key=lambda x: (x.get("points", 0) or x.get("score", 0), x.get("comments", 0)),
        reverse=True,
    )

    return {
        "fetched_at": datetime.now().isoformat(),
        "total_signals": len(all_posts),
        "sources": {
            "hacker_news": len(hn_posts),
            "lobsters": len(lobsters_posts),
            "github_trending": len(github_posts),
            "reddit": len(reddit_posts),
            "product_hunt": len(ph_posts),
        },
        "posts": all_posts[:40],
    }


def analyze_top_opportunities(posts: list, top_n: int = 3, monitor: OpportunityMonitor = None):
    print_header(f"En İyi {top_n} Fırsat")

    candidates = [p for p in posts if is_likely_opportunity(p.get("title", ""))]

    if len(candidates) < top_n:
        print(f"  (Filtrelenmiş aday: {len(candidates)} — tüm listeye bakılıyor)")
        candidates = posts
    else:
        print(f"  (Filtrelenmiş aday: {len(candidates)})")

    results = []

    for i, post in enumerate(candidates[:top_n], 1):
        title = post.get("title", "")
        source = post.get("source", "")
        points = post.get("points", 0) or post.get("score", 0)
        comments = post.get("comments", 0)
        url = post.get("url", "")

        signals = analyze_post(post)
        score_result = calculate_opportunity_score(signals)

        rationale = generate_rationale(
            title=title,
            source=source,
            points=points,
            comments=comments,
            score_breakdown=result_to_dict(score_result)["breakdown"],
            language="tr",
        )

        print_opportunity(i, post, score_result, rationale)

        if monitor and score_result.total_score >= 65:
            monitor.track(
                title=title,
                url=url,
                source=source,
                score=score_result.total_score,
                notes="Otomatik takip (skor ≥ 65)",
            )

        results.append({
            "title": title,
            "source": source,
            "points": points,
            "score": result_to_dict(score_result),
            "rationale": rationale,
        })

    return results


def save_json(data: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 Kaydedildi → {filename}")


if __name__ == "__main__":
    print("\n" + "█" * 64)
    print("  AI OPPORTUNITY HUNTER")
    print("  Solo Founder Fırsat Karar Motoru")
    print("█" * 64)

    monitor = OpportunityMonitor()

    signals = fetch_all_signals(limit_per_source=10)
    save_json(signals, "daily_signals.json")

    analyze_top_opportunities(signals["posts"], top_n=3, monitor=monitor)

    print_header("Opportunity Monitor Özeti")
    print(monitor.summary())

    print("\n" + "█" * 64)
    print("  Tamamlandı.")
    print("█" * 64 + "\n")
