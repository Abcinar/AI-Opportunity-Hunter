import sys
import logging

# Proje içi modüller (Mevcut mimarinize göre yolları güncelleyebilirsiniz)
from engine.collector import collect_signals
from engine.normalizer import normalize_posts
from engine.intelligence import analyze_signals
from engine.scorer import calculate_score
from engine.recommender import recommend
from engine.exporter import save_daily_signals, save_opportunities


def main():
    # ÇÖZÜM 4: İzlenebilirlik için Logging konfigürasyonu eklendi
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    print("================================================================")
    print("  AI Opportunity Hunter - Startup Decision Engine V1")
    print("================================================================\n")

    # ÇÖZÜM 1: Ağ ve veri hatalarına karşı tüm pipeline Try-Except içine alındı
    try:
        # STEP 1 Collect
        # ÇÖZÜM 1: Ağ ve veri hatalarına karşı tüm pipeline Try-Except içine alındı
    try:
        # STEP 1 Collect
        print("[1/6] Collecting signals...")
        raw_signals = collect_signals()

        # STEP 2 Normalize
        print("\n[2/6] Normalizing signals...")
        
        # Gelen veri bir sözlük (dict) ise, önce içindeki tüm listeleri
        # birleştirerek tek boyutlu (flat) bir liste haline getiriyoruz.
        if isinstance(raw_signals, dict):
            flat_signals = []
            for items in raw_signals.values():
                if isinstance(items, list):
                    flat_signals.extend(items)
            normalized = normalize_posts(flat_signals)
        else:
            normalized = normalize_posts(raw_signals)

        # STEP 3 Analyze (Bu kısım ve aşağısı else: bloğu ile aynı hizada olmalı)
        print("\n[3/6] Building evidence...")
        analyses = analyze_signals(normalized)

        # STEP 4 Score + Recommend
        print("\n[4/6] Calculating opportunity scores...")
        opportunities = []

        for signal, analysis in zip(normalized, analyses):

            # ÇÖZÜM 3: Intelligence verisi dict veya obje (dataclass) ise güvenle okuma garantisi
            if isinstance(analysis, dict):
                intelligence = analysis.get("intelligence", analysis)
            elif hasattr(analysis, "intelligence"):
                intelligence = getattr(analysis, "intelligence")
            else:
                intelligence = analysis

            signal["intelligence"] = intelligence

            score_result = calculate_score(signal)
            recommendation = recommend(score_result)

            # ÇÖZÜM 2: Tip Uyuşmazlığına karşı 'evidence' değişkeninin güvenli ayrıştırılması
            evidence_data = intelligence.get("evidence", {}) if isinstance(intelligence, dict) else {}

            opportunity = {
                **signal,
                "intelligence": intelligence,
                "analysis": {
                    "score": score_result,
                    "decision": recommendation,
                    "evidence": evidence_data,
                },
            }

            opportunities.append(opportunity)

        opportunities.sort(
            key=lambda x: x.get("analysis", {}).get("score", {}).get("overall_score", 0),
            reverse=True,
        )

        # STEP 5 Export
        print("\n[5/6] Exporting opportunities...")
        save_daily_signals(normalized)
        save_opportunities(opportunities)

    except Exception as e:
    # STEP 6 Summary
    print("\n[6/6] Final Summary\n")
    
    distribution = {"BUILD": 0, "INVESTIGATE": 0, "WATCH": 0, "SKIP": 0}
    
    for opp in opportunities:
        analysis = opp.get("analysis", {})
        dec_data = analysis.get("decision", {})
        score_data = analysis.get("score", {})
        
        if isinstance(dec_data, dict):
            dec_val = dec_data.get("decision", "SKIP")
        elif isinstance(dec_data, str):
            dec_val = dec_data
        elif isinstance(score_data, dict):
            dec_val = score_data.get("decision", "SKIP")
        else:
            dec_val = "SKIP"
            
        if dec_val in distribution:
            distribution[dec_val] += 1
        else:
            distribution["SKIP"] += 1

    print("Decision Distribution")
    print(f"🚀 BUILD        : {distribution['BUILD']}")
    print(f"🔍 INVESTIGATE  : {distribution['INVESTIGATE']}")
    print(f"👀 WATCH        : {distribution['WATCH']}")
    print(f"❌ SKIP         : {distribution['SKIP']}\n")

    print("================================================================")
    print("  Top 5 Opportunities")
    print("================================================================")

    for i, opp in enumerate(opportunities[:5], 1):
        analysis = opp.get("analysis", {})
        decision_data = analysis.get("decision", {})
        score_data = analysis.get("score", {})

        if isinstance(decision_data, dict):
            decision_val = decision_data.get("decision", "SKIP")
            overall_score = decision_data.get("overall_score", 0)
            confidence = decision_data.get("confidence", 0.0)
        elif isinstance(decision_data, str):
            decision_val = decision_data
            overall_score = 0
            confidence = 0.0
        else:
            decision_val = "SKIP"
            overall_score = 0
            confidence = 0.0

        if overall_score == 0 and isinstance(score_data, dict):
            overall_score = score_data.get("overall_score", 0)
            if decision_val == "SKIP" or not decision_val:
                decision_val = score_data.get("decision", "SKIP")
            confidence = score_data.get("confidence", 0.0)

        emoji_map = {
            "BUILD": "🚀",
            "INVESTIGATE": "✅",
            "WATCH": "🔭",
            "SKIP": "❌",
        }
        emoji = emoji_map.get(decision_val, "❌")
        
        title = str(opp.get("title", "No Title"))[:80]
        
        print(f"\n[{i}] {emoji} {title}")
        print(f"    Source     : {opp.get('source', 'unknown')}")
        print(f"    Score      : {overall_score}/100")
        print(f"    Confidence : {confidence * 100:.1f}%")
        print(f"    Decision   : {decision_val}")

    print("\n################################################################")
    print("  Pipeline completed successfully.")
    print("################################################################")


if __name__ == "__main__":
    main()
