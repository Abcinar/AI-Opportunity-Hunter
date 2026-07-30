import math
from typing import Dict, Any, Union, List

try:
    from config import SCORING_WEIGHTS
except ImportError:
    # Config modülü bulunamazsa veya eksikse varsayılan ağırlıklar
    SCORING_WEIGHTS = {
        "evidence": 0.30,
        "timing": 0.20,
        "market": 0.20,
        "execution": 0.15,
        "competition": 0.15
    }

def _safe_get(data: Any, key: str, default: Any = None) -> Any:
    """Sözlük içerisinden güvenli bir şekilde veri çeker."""
    if isinstance(data, dict):
        return data.get(key, default)
    return default

def _parse_level(value: Any, default: int = 50) -> int:
    """String veya sayısal metrikleri 0-100 arası standart puana dönüştürür."""
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value <= 1.0:
            return int(value * 100)
        return max(0, min(int(value), 100))
    
    if isinstance(value, str):
        v = value.lower()
        if any(x in v for x in ["high", "strong", "excellent", "blue ocean", "large", "b2b", "massive"]):
            return 85
        if any(x in v for x in ["medium", "moderate", "good", "niche", "prosumer", "b2b2c"]):
            return 50
        if any(x in v for x in ["low", "weak", "poor", "red ocean", "b2c", "small", "hard"]):
            return 20
    return default

def _score_evidence(evidence: Any) -> int:
    """Kanıt (Evidence) alanını skorlar (Maks 100)."""
    score = 0
    has_pain = str(_safe_get(evidence, "has_clear_pain", False)).lower()
    has_workaround = str(_safe_get(evidence, "has_workaround", False)).lower()
    count = _safe_get(evidence, "evidence_count", 0)

    if has_pain in ["true", "1", "yes", "t"]:
        score += 40
    if has_workaround in ["true", "1", "yes", "t"]:
        score += 30

    try:
        c = int(count)
        score += min(c * 10, 30)
    except (ValueError, TypeError):
        pass
    
    return min(max(score, 0), 100)

def _score_timing(trend_dict: Any, why_now_dict: Any) -> int:
    """Zamanlama ve trend gücünü skorlar (Maks 100)."""
    trend_val = _safe_get(trend_dict, "trend_strength", "medium")
    why_now_val = _safe_get(why_now_dict, "why_now_strength", "medium")
    
    trend_score = _parse_level(trend_val)
    why_now_score = _parse_level(why_now_val)
    
    return int((trend_score * 0.5) + (why_now_score * 0.5))

def _score_market(market_dict: Any, category_dict: Any, business_models: Any) -> int:
    """Pazar türü, boyutu ve iş modelini skorlar (Maks 100)."""
    m_type = _parse_level(_safe_get(market_dict, "market_type", "medium"))
    m_size = _parse_level(_safe_get(market_dict, "market_size", "medium"))
    
    # Kategori ve Business Model varlığı ek bonus sağlar (+10)
    bonus = 0
    cat_val = _safe_get(category_dict, "primary_category")
    if cat_val and str(cat_val).strip() != "":
        bonus += 5
        
    if isinstance(business_models, list) and len(business_models) > 0:
        bonus += 5
    elif isinstance(business_models, dict) and business_models:
        bonus += 5
        
    base_score = int((m_type * 0.5) + (m_size * 0.5))
    return min(base_score + bonus, 100)

def _score_execution(fit_dict: Any, opp_dict: Any) -> int:
    """Kurucu uyumu ve ürün zorluk derecesini skorlar (Maks 100)."""
    fit_val = _parse_level(_safe_get(fit_dict, "founder_fit_level", "medium"))
    
    # Zorluk ters orantılıdır (Yüksek zorluk = Düşük skor)
    diff_raw = _parse_level(_safe_get(opp_dict, "difficulty", "medium"))
    diff_score = 100 - diff_raw if diff_raw > 0 else 50
    
    return int((fit_val * 0.6) + (diff_score * 0.4))

def _score_competition(comp_dict: Any) -> int:
    """Rekabet düzeyini skorlar. (Ters orantılı: Yüksek rekabet = Düşük skor)"""
    comp_raw = _parse_level(_safe_get(comp_dict, "competition_level", "medium"))
    return 100 - comp_raw if comp_raw > 0 else 50

def calculate_score(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    V3 Intelligence verisini Scorer V2 mimarisi ile detaylı analiz eder.
    Tüm alanlar modüler olarak puanlanır ve ağırlıklı genel skor üretilir.
    """
    intelligence = signal.get("intelligence", {})
    
    # Sözlük bloklarının çekilmesi
    evidence_dict = intelligence.get("evidence", {})
    trend_dict = intelligence.get("trend_strength", {})
    market_dict = intelligence.get("market_type", {})
    why_now_dict = intelligence.get("why_now", {})
    category_dict = intelligence.get("category", {})
    business_models = intelligence.get("business_models", [])
    fit_dict = intelligence.get("founder_fit", {})
    opp_dict = intelligence.get("opportunity", {})
    comp_dict = intelligence.get("competition_level", {})
    
    # Alt Modül Skorlamaları
    evidence_score = _score_evidence(evidence_dict)
    timing_score = _score_timing(trend_dict, why_now_dict)
    market_score = _score_market(market_dict, category_dict, business_models)
    execution_score = _score_execution(fit_dict, opp_dict)
    competition_score = _score_competition(comp_dict)
    
    # Güven Skoru (Confidence) - 0.0-1.0 aralığını 0.0-100.0 aralığına çevirir
    raw_confidence = intelligence.get("confidence_score", 0.0)
    try:
        if isinstance(raw_confidence, dict):
            confidence_val = float(raw_confidence.get("confidence_score", 0.0))
        else:
            confidence_val = float(raw_confidence)
            
        # Eğer zaten 1.0'dan büyük gelirse (örneğin 80.0) tekrar çarpmamak için düzeltme
        if confidence_val > 1.0:
            confidence_val = confidence_val / 100.0
            
        confidence = max(0.0, min(confidence_val, 1.0)) * 100.0
    except (ValueError, TypeError):
        confidence = 0.0

    # Ağırlıkları config'den çek
    w_evidence = SCORING_WEIGHTS.get("evidence", 0.30)
    w_timing = SCORING_WEIGHTS.get("timing", 0.20)
    w_market = SCORING_WEIGHTS.get("market", 0.20)
    w_execution = SCORING_WEIGHTS.get("execution", 0.15)
    w_competition = SCORING_WEIGHTS.get("competition", 0.15)

    # Ağırlıklı Genel Skor (Overall Score)
    overall_score = int(
        (evidence_score * w_evidence) +
        (timing_score * w_timing) +
        (market_score * w_market) +
        (execution_score * w_execution) +
        (competition_score * w_competition)
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

    # Breakdown için raw dataların çıkarılması
    return {
        "overall_score": overall_score,
        "confidence": round(confidence, 1),
        "breakdown": {
            "scores": {
                "evidence_score": evidence_score,
                "timing_score": timing_score,
                "market_score": market_score,
                "execution_score": execution_score,
                "competition_score": competition_score
            },
            "raw_data": {
                "has_clear_pain": _safe_get(evidence_dict, "has_clear_pain"),
                "has_workaround": _safe_get(evidence_dict, "has_workaround"),
                "evidence_count": _safe_get(evidence_dict, "evidence_count"),
                "trend_strength": _safe_get(trend_dict, "trend_strength"),
                "market_type": _safe_get(market_dict, "market_type"),
                "market_size": _safe_get(market_dict, "market_size"),
                "target_customer": _safe_get(market_dict, "target_customer"),
                "competition_level": _safe_get(comp_dict, "competition_level"),
                "founder_fit_level": _safe_get(fit_dict, "founder_fit_level"),
                "why_now_strength": _safe_get(why_now_dict, "why_now_strength"),
                "primary_category": _safe_get(category_dict, "primary_category"),
                "product_type": _safe_get(opp_dict, "product_type"),
                "difficulty": _safe_get(opp_dict, "difficulty")
            }
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
        return calculate_score(signal)
