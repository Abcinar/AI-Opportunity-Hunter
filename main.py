# ================================================================
# BURALAR EKSİK: Kütüphane importları, config dosyaları
# ================================================================
import json
# Diğer importların...

# ================================================================
# BURALAR EKSİK: Adım 1 (Collect), Adım 2 (Normalize), Adım 3 (Analyze) 
# kodlarının bulunduğu 150-200 satırlık orijinal kısımlar.
# ================================================================

def main():
    # ... (Adım 1, 2, 3 kodları) ...

    # [4/6] Calculating opportunity scores...
    opportunities = []
    
    for signal, analysis in zip(normalized, analyses):
        if not isinstance(analysis, dict):
            analysis = {}

        intelligence = analysis.get("intelligence", analysis)
        signal["intelligence"] = intelligence

        score_result = calculate_score(signal)
        recommendation = recommend(score_result)

        opportunity = {
            **signal,
            "intelligence": intelligence,
            "analysis": {
                "score": score_result,
                "decision": recommendation,
                "evidence": intelligence.get("evidence", {}),
            },
        }

        opportunities.append(opportunity)

    opportunities.sort(
        key=lambda x: x.get("analysis", {})
                       .get("decision", {})
                       .get("overall_score", 0),
        reverse=True,
    )

    # ================================================================
    # BURALAR EKSİK: Adım 5 (Export) kısmı
    # ================================================================
    # [5/6] Exporting opportunities...
    # with open("data/opportunities.json", "w") as f: ...

    # [6/6] Final Summary ve Yazdırma (Emojileri düzelttiğimiz yer)
    for opp in opportunities:
        decision = opp.get("analysis", {}).get("decision", {})
        confidence_raw = decision.get("confidence", 0.0) 
        score = decision.get("overall_score", 0)
        decision_val = decision.get("decision", "SKIP")
        
        emoji_map = {
            "BUILD": "🚀",
            "INVESTIGATE": "✅",
            "WATCH": "🔭",
            "SKIP": "❌",
        }
        emoji = emoji_map.get(decision_val, "•")
        
        print(f"[{emoji}] {opp.get('title', 'No Title')}")
        print(f"    Score      : {score}/100")
        print(f"    Confidence : {confidence_raw * 100:.1f}%")
        print(f"    Decision   : {decision_val}")
        # ...

if __name__ == "__main__":
    main()
