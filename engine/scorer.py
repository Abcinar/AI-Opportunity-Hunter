import math
from typing import Dict, Any

def _parse_metric(value: Any, default: int = 50) -> int:
    """
    Intelligence verilerini normalize eder (0-100).
    """
    if isinstance(value, (int, float)):
        # Eğer 0.0 - 1.0 aralığındaysa 100 ile çarp
        if isinstance(value, float) and value <= 1.0:
            return int(value * 100)
        return max(0, min(int(value), 100))
    
    if isinstance(value, str):
        val_lower = value.lower()
        if val_lower in ["high", "strong", "excellent", "blue ocean"]:
            return 85
        if val_lower in ["medium", "moderate", "good", "niche"]:
            return 50
        if val_lower in ["low", "weak", "poor", "red ocean"]:
            return 20
            
    return default

def calculate_opportunity_score(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    V3 Intelligence verisini kullanarak final skor ve kararı (Decision) üretir.
    Eski V1 sahte evidence üretimleri ve hardcoded değerler kaldırılmıştır.
    """
    intelligence = signal.get("intelligence", {})
    
    # Intelligence'dan doğrudan okunan metrikler
    trend_strength = intelligence.get("trend_strength")
    competition_level = intelligence.get("competition_level")
    founder_fit = intelligence.get("founder_fit")
    market_type = intelligence.get("market_type", "Unknown")
    why_now = intelligence.get("why_now", "Unknown")
    evidence = intelligence.get("evidence", [])
    
    # Güven skoru: Doğrudan 0.00 - 1.00 arası float olarak alınıp korunur
    raw_confidence = intelligence.get("confidence_score", 0.0)
    try:
        confidence = max(0.0, min(float(raw_confidence), 1.0))
    except (ValueError, TypeError):
        confidence = 0.0

    # Alt skorların hesaplanması
    trend_score = _parse_metric(trend_strength, default=50)
    fit_score = _parse_metric(founder_fit, default=50)
    
    # Rekabet skoru ters orantılıdır (Yüksek rekabet = Düşük skor)
    comp_raw = _parse_metric(competition_level, default=50)
    comp_score = 100 - comp_raw if comp_raw > 0 else 50
    
    # Evidence sayısı çarpanı (Maksimum 100)
    evidence_count = len(evidence) if isinstance(evidence, list) else 0
    evidence_score = min(evidence_count * 20, 100)

    # Ağırlıklı Genel Skor (Overall Score)
    overall_score = int(
        (trend_score * 0.35) +
        (comp_score * 0.25) +
        (fit_score * 0.25) +
        (evidence_score * 0.15)
    )
    
    overall_score = max(0, min(overall_score, 100))

    # Karar (Decision) Eşikleri
    if overall_score >= 90:
        decision = "BUILD"
    elif overall_score >= 70:
        decision = "INVESTIGATE"
    elif overall_score >= 50:
        decision = "WATCH"
    else:
        decision = "SKIP"

    return {
        "overall_score": overall_score,
        "confidence": confidence,
        "breakdown": {
            "trend_score": trend_score,
            "competition_score": comp_score,
            "founder_fit_score": fit_score,
            "evidence_score": evidence_score,
            "market_type": market_type,
            "why_now": why_now,
            "evidence_count": evidence_count
        },
        "decision": decision
    }

class Scorer:
    """
    Ana Pipeline'da kullanılacak sınıf sarmalayıcısı.
    """
    def __init__(self):
        pass

    def evaluate(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        return calculate_opportunity_score(signal)
