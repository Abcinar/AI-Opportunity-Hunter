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
