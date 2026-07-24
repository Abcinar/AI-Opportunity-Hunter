"""
AI Opportunity Hunter
Main Pipeline
"""

from engine.collector import collect_signals
from engine.normalizer import normalize_posts
from engine.intelligence import analyze_signals
from engine.scorer import calculate_score
from engine.recommender import recommend
from engine.exporter import export_json


def main():

    print("=" * 60)
    print("AI Opportunity Hunter")
    print("=" * 60)

    # -------------------------------------------------
    # STEP 1
    # -------------------------------------------------

    print("\n[1/6] Collecting signals...")

    raw = collect_signals()

    print(f"Collected : {len(raw)} signals")

    # -------------------------------------------------
    # STEP 2
    # -------------------------------------------------

    print("\n[2/6] Normalizing...")

    normalized = normalize_posts(raw)

    # -------------------------------------------------
    # STEP 3
    # -------------------------------------------------

    print("\n[3/6] Building evidence...")

    analyses = analyze_signals(normalized)

    # -------------------------------------------------
    # STEP 4
    # -------------------------------------------------

    print("\n[4/6] Calculating scores...")

    opportunities = []

    for signal, analysis in zip(normalized, analyses):

        score = calculate_score(
            analysis["evidence"]
        )

        decision = recommend(score)

        opportunities.append({

            **signal,

            "analysis": {

                "score": score,

                "decision": decision,

                "evidence": analysis["evidence"]

            }

        })

    # -------------------------------------------------
    # STEP 5
    # -------------------------------------------------

    print("\n[5/6] Exporting...")

    export_json(
        opportunities,
        "data/opportunities.json"
    )

    # -------------------------------------------------
    # STEP 6
    # -------------------------------------------------

    build = sum(
        1
        for o in opportunities
        if o["analysis"]["decision"]["decision"] == "BUILD"
    )

    print("\n[6/6] Done")

    print()

    print("=" * 60)

    print(f"Total Opportunities : {len(opportunities)}")

    print(f"BUILD              : {build}")

    print("=" * 60)


if __name__ == "__main__":
    main()
