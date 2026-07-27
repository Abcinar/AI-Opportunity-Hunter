"""
AI Opportunity Hunter
Startup Decision Engine V1

Pipeline:
Collect → Normalize → Analyze → Score → Recommend → Export
"""

from engine.collector import collect_signals
from engine.normalizer import normalize_posts
from engine.intelligence import analyze_signals
from engine.scorer import calculate_score
from engine.recommender import recommend
from engine.exporter import (
    save_daily_signals,
    save_opportunities,
)


# --------------------------------------------------
# Console Helpers
# --------------------------------------------------

def print_header(title: str):
    print("\n" + "=" * 64)
    print(f"  {title}")
    print("=" * 64)


def print_opportunity(index: int, opportunity: dict):

    analysis = opportunity["analysis"]
    decision = analysis["decision"]

    score = decision["overall_score"]
    confidence = decision["confidence"]

    emoji_map = {
        "BUILD": "🚀",
        "INVESTIGATE": "🔍",
        "WATCH": "👀",
        "SKIP": "❌",
    }

    emoji = emoji_map.get(decision["decision"], "•")

    print(f"\n[{index}] {emoji} {opportunity['title'][:70]}")
    print(f"    Source     : {opportunity['source']}")
    print(f"    Score      : {score}/100")
    print(f"    Confidence : {confidence}%")
    print(f"    Decision   : {decision['decision']}")

    print("    Evidence   :")

    for ev in analysis["evidence"]:
        level = ev["level"].replace("_", " ").title()
        print(f"      ✓ {ev['type'].replace('_',' ').title()} → {level}")


# --------------------------------------------------
# Main Pipeline
# --------------------------------------------------

def main():

    print_header("AI Opportunity Hunter - Startup Decision Engine V1")

    # --------------------------------------------------
    # STEP 1 - Collect
    # --------------------------------------------------

    print("\n[1/6] Collecting signals...")

    signals = collect_signals()

    save_daily_signals(signals)

    print(f"Collected: {signals['total_signals']} signals")

    # --------------------------------------------------
    # STEP 2 - Normalize
    # --------------------------------------------------

    print("\n[2/6] Normalizing signals...")

    normalized = normalize_posts(signals["posts"])

    print(f"Normalized: {len(normalized)} signals")

    # --------------------------------------------------
    # STEP 3 - Analyze
    # --------------------------------------------------

    print("\n[3/6] Building evidence...")

    analyses = analyze_signals(normalized)

    print(f"Analyzed: {len(analyses)} opportunities")

    # --------------------------------------------------
    # STEP 4 - Score + Recommend
    # --------------------------------------------------

    print("\n[4/6] Calculating opportunity scores...")

    opportunities = []

    for signal, analysis in zip(normalized, analyses):

        score_result = calculate_score(
            analysis["evidence"]
        )

        recommendation = recommend(score_result)

        opportunity = {
            **signal,
            "analysis": {
                "score": score_result,
                "decision": recommendation,
                "evidence": analysis["evidence"],
            },
        }

        opportunities.append(opportunity)

    # En yüksek skora göre sırala
    opportunities.sort(
        key=lambda x: x["analysis"]["decision"]["overall_score"],
        reverse=True,
    )

    # --------------------------------------------------
    # STEP 5 - Export
    # --------------------------------------------------

    print("\n[5/6] Exporting opportunities...")

    save_opportunities(opportunities)

    print("Saved: data/opportunities.json")

    # --------------------------------------------------
    # STEP 6 - Summary
    # --------------------------------------------------

    print("\n[6/6] Final Summary")

    build_count = sum(
        1 for o in opportunities
        if o["analysis"]["decision"]["decision"] == "BUILD"
    )

    investigate_count = sum(
        1 for o in opportunities
        if o["analysis"]["decision"]["decision"] == "INVESTIGATE"
    )

    watch_count = sum(
        1 for o in opportunities
        if o["analysis"]["decision"]["decision"] == "WATCH"
    )

    skip_count = sum(
        1 for o in opportunities
        if o["analysis"]["decision"]["decision"] == "SKIP"
    )

    print("\nDecision Distribution")
    print(f"🚀 BUILD        : {build_count}")
    print(f"🔍 INVESTIGATE  : {investigate_count}")
    print(f"👀 WATCH        : {watch_count}")
    print(f"❌ SKIP         : {skip_count}")

    # --------------------------------------------------
    # TOP 5
    # --------------------------------------------------

    print_header("Top 5 Opportunities")

    for i, opportunity in enumerate(opportunities[:5], start=1):
        print_opportunity(i, opportunity)

    print("\n" + "#" * 64)
    print("  Pipeline completed successfully.")
    print("#" * 64 + "\n")


# --------------------------------------------------
# Entry Point
# --------------------------------------------------

if __name__ == "__main__":
    main()
