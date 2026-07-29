"""
main.py
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

    analysis = opportunity.get("analysis", {})
    decision = analysis.get("decision", {})

    score = decision.get("overall_score", 0)
    confidence = decision.get("confidence", 0)
    decision_val = decision.get("decision", "SKIP")

    emoji_map = {
        "BUILD": "🚀",
        "INVESTIGATE": "🔍",
        "WATCH": "👀",
        "SKIP": "❌",
    }

    emoji = emoji_map.get(decision_val, "•")

    title = opportunity.get('title', '')[:70]
    source = opportunity.get('source', 'Unknown')

    print(f"\n[{index}] {emoji} {title}")
    print(f"    Source     : {source}")
    print(f"    Score      : {score}/100")
    print(f"    Confidence : {confidence}%")
    print(f"    Decision   : {decision_val}")

    print("    Evidence   :")

    evidence_data = analysis.get("evidence", [])
    
    # Geriye dönük uyumluluk ve yeni V2 yapısı için güvenli döngü
    if isinstance(evidence_data, list):
        for ev in evidence_data:
            if isinstance(ev, dict):
                level = ev.get("level", "unknown").replace("_", " ").title()
                ev_type = ev.get("type", "unknown").replace("_", " ").title()
                print(f"      ✓ {ev_type} → {level}")
    elif isinstance(evidence_data, dict):
        for key, value in evidence_data.items():
            key_formatted = str(key).replace("_", " ").title()
            print(f"      ✓ {key_formatted} → {value}")


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
    if not isinstance(signals, dict):
        signals = {"total_signals": 0, "posts": []}

    save_daily_signals(signals)

    total_signals = signals.get('total_signals', 0)
    print(f"Collected: {total_signals} signals")

    # --------------------------------------------------
    # STEP 2 - Normalize
    # --------------------------------------------------

    print("\n[2/6] Normalizing signals...")

    posts = signals.get("posts", [])
    normalized = normalize_posts(posts)

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
        
        if not isinstance(analysis, dict):
            analysis = {}

        # V2 intelligence yapısını güvenli bir şekilde kontrol et
        intelligence = analysis.get("intelligence", analysis)
        evidence = intelligence.get("evidence", {})

        score_result = calculate_score(evidence)
        recommendation = recommend(score_result)

        opportunity = {
            **signal,
            "analysis": {
                "score": score_result,
                "decision": recommendation,
                "evidence": evidence,
            },
        }

        opportunities.append(opportunity)

    # En yüksek skora göre sırala
    opportunities.sort(
        key=lambda x: x.get("analysis", {}).get("decision", {}).get("overall_score", 0),
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
        if o.get("analysis", {}).get("decision", {}).get("decision") == "BUILD"
    )

    investigate_count = sum(
        1 for o in opportunities
        if o.get("analysis", {}).get("decision", {}).get("decision") == "INVESTIGATE"
    )

    watch_count = sum(
        1 for o in opportunities
        if o.get("analysis", {}).get("decision", {}).get("decision") == "WATCH"
    )

    skip_count = sum(
        1 for o in opportunities
        if o.get("analysis", {}).get("decision", {}).get("decision") == "SKIP"
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
