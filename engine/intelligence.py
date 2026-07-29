"""
Opportunity Intelligence Engine V3 (Production Ready)
-----------------------------------------------------
AI Opportunity Hunter projesinin analiz katmanı.
Sinyalleri alır, anlamlandırır ve yapılandırılmış zeka (intelligence) üretir.
Tamamen Rule-Based V1 mimarisiyle çalışır.

Modüler yapıya geçilmiştir. Kurallar (rules/), veri modelleri (models.py)
ve ayarlar (config.py) dışarıdan import edilir.
Asla skor, öncelik veya öneri üretmez. JSON uyumlu veri döndürür.
"""

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List
from dataclasses import asdict

# Dışa aktarılmış yapılandırma ve modeller (Proje dizininde var olduğu varsayılır)
from config import (
    INTELLIGENCE_ENGINE_VERSION,
    RULES_VERSION,
    TREND_HIGH_ENGAGEMENT_THRESHOLD,
    TREND_MEDIUM_ENGAGEMENT_THRESHOLD,
    CONFIDENCE_WEIGHTS
)
from engine.models import (
    TrendStrength,
    MarketType,
    CompetitionLevel,
    FounderFitLevel,
    OpportunityIdea
)
from engine.rules.pain_rules import PAIN_KEYWORDS, SOLUTION_KEYWORDS
from engine.rules.category_rules import CATEGORIES, SUB_CATEGORIES
from engine.rules.market_rules import B2B_KEYWORDS, B2C_KEYWORDS, TARGET_CUSTOMERS, MARKET_SIZE_INDICATORS
from engine.rules.business_rules import BUSINESS_MODELS
from engine.rules.competition_rules import HIGH_COMPETITION_KEYWORDS, LOW_COMPETITION_KEYWORDS
from engine.rules.opportunity_rules import PRODUCT_TYPES, DELIVERY_METHODS
from engine.rules.founder_rules import RED_FLAGS, GREEN_FLAGS
from engine.rules.why_now_rules import URGENCY_KEYWORDS

# Loglama yapılandırması
logger = logging.getLogger(__name__)


class BaseEngine:
    """Tüm motorlar için temel yardımcı fonksiyonları barındıran üst sınıf."""
    
    @staticmethod
    def _count_keywords(text: str, keywords: List[str]) -> int:
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower)
    
    @staticmethod
    def _extract_sentences(text: str, keywords: List[str]) -> List[str]:
        sentences = re.split(r'(?<=[.!?]) +', text)
        matched = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in keywords):
                matched.append(sentence.strip())
        return matched

    @staticmethod
    def _find_matched_keywords(text: str, keywords: List[str]) -> List[str]:
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower]


class EvidenceEngine(BaseEngine):
    """Sinyal içindeki somut kanıtları tespit eder."""

    def analyze(self, text: str) -> Dict[str, Any]:
        logger.debug("EvidenceEngine çalıştırılıyor...")
        pain_points = self._extract_sentences(text, PAIN_KEYWORDS)
        solutions = self._extract_sentences(text, SOLUTION_KEYWORDS)
        
        return {
            "has_clear_pain": len(pain_points) > 0,
            "has_workaround": len(solutions) > 0,
            "extracted_pain_points": pain_points,
            "extracted_solutions": solutions,
            "evidence_count": len(pain_points) + len(solutions)
        }


class CategoryEngine(BaseEngine):
    """Sinyali ana kategoriye ve alt kategoriye ayırır."""

    def analyze(self, text: str, tags: List[str]) -> Dict[str, str]:
        logger.debug("CategoryEngine çalıştırılıyor...")
        combined_text = f"{text} {' '.join(tags)}".lower()
        
        primary_category = "Uncategorized"
        max_matches = 0
        for cat, keywords in CATEGORIES.items():
            matches = self._count_keywords(combined_text, keywords)
            if matches > max_matches:
                max_matches = matches
                primary_category = cat
                
        sub_category = "General"
        max_sub_matches = 0
        for sub, keywords in SUB_CATEGORIES.items():
            matches = self._count_keywords(combined_text, keywords)
            if matches > max_sub_matches:
                max_sub_matches = matches
                sub_category = sub
                
        return {
            "primary_category": primary_category,
            "sub_category": sub_category
        }


class TrendEngine(BaseEngine):
    """Sinyalin etkileşim metriklerine göre trend gücünü belirler."""

    def analyze(self, upvotes: int, comments: int) -> Dict[str, str]:
        logger.debug("TrendEngine çalıştırılıyor...")
        total_engagement = upvotes + (comments * 2)
        
        if total_engagement >= TREND_HIGH_ENGAGEMENT_THRESHOLD:
            trend_strength = TrendStrength.STRONG
        elif total_engagement >= TREND_MEDIUM_ENGAGEMENT_THRESHOLD:
            trend_strength = TrendStrength.MODERATE
        else:
            trend_strength = TrendStrength.WEAK
            
        return {
            "trend_strength": trend_strength.value,
            "engagement_tier": trend_strength.value
        }


class MarketEngine(BaseEngine):
    """Pazar tipini (B2B/B2C) ve hedef kitleyi analiz eder."""

    def analyze(self, text: str) -> Dict[str, str]:
        logger.debug("MarketEngine çalıştırılıyor...")
        text_lower = text.lower()
        
        b2b_score = self._count_keywords(text_lower, B2B_KEYWORDS)
        b2c_score = self._count_keywords(text_lower, B2C_KEYWORDS)
        
        market_type = MarketType.HYBRID
        if b2b_score > b2c_score:
            market_type = MarketType.B2B
        elif b2c_score > b2b_score:
            market_type = MarketType.B2C
            
        target_customer = "General"
        max_target_matches = 0
        for audience, keywords in TARGET_CUSTOMERS.items():
            matches = self._count_keywords(text_lower, keywords)
            if matches > max_target_matches:
                max_target_matches = matches
                target_customer = audience
                
        market_size = "Medium"
        niche_score = self._count_keywords(text_lower, MARKET_SIZE_INDICATORS["Niche"])
        large_score = self._count_keywords(text_lower, MARKET_SIZE_INDICATORS["Large"])
        
        if niche_score > large_score:
            market_size = "Niche"
        elif large_score > niche_score:
            market_size = "Large"
            
        return {
            "market_type": market_type.value,
            "target_customer": target_customer,
            "market_size": market_size
        }


class BusinessModelEngine(BaseEngine):
    """Uygun iş modellerini ağırlıklı olarak tahmin eder."""

    def analyze(self, text: str) -> Dict[str, float]:
        logger.debug("BusinessModelEngine çalıştırılıyor...")
        model_scores = {}
        text_lower = text.lower()
        total_keywords_found = 0
        raw_scores = {}
        
        for model, keywords in BUSINESS_MODELS.items():
            matches = self._count_keywords(text_lower, keywords)
            raw_scores[model] = matches
            total_keywords_found += matches
            
        if total_keywords_found == 0:
            return {"SaaS": 0.5, "Undetermined": 1.0}
            
        for model, score in raw_scores.items():
            if score > 0:
                confidence = min(1.0, (score / total_keywords_found) + (score * 0.1))
                model_scores[model] = round(confidence, 2)
                
        return dict(sorted(model_scores.items(), key=lambda item: item[1], reverse=True))


class CompetitionEngine(BaseEngine):
    """Rekabet düzeyini ve nedenlerini analiz eder."""

    def analyze(self, text: str) -> Dict[str, Any]:
        logger.debug("CompetitionEngine çalıştırılıyor...")
        text_lower = text.lower()
        
        high_matched = self._find_matched_keywords(text_lower, HIGH_COMPETITION_KEYWORDS)
        low_matched = self._find_matched_keywords(text_lower, LOW_COMPETITION_KEYWORDS)
        
        competition_level = CompetitionLevel.MEDIUM
        reason = "No strong competition indicators found."
        matched_keywords = []
        
        if len(high_matched) > len(low_matched):
            competition_level = CompetitionLevel.HIGH
            reason = "Mentions direct competitors or alternative solutions."
            matched_keywords = high_matched
        elif len(low_matched) > len(high_matched):
            competition_level = CompetitionLevel.LOW
            reason = "Indicates a lack of existing solutions or tools."
            matched_keywords = low_matched
            
        return {
            "competition_level": competition_level.value,
            "reason": reason,
            "matched_keywords": matched_keywords
        }


class ProblemEngine(BaseEngine):
    """Sinyalin işaret ettiği temel problemi, hedef kitle ile birleştirerek özetler."""

    def analyze(self, evidence_data: Dict[str, Any], market_data: Dict[str, str]) -> str:
        logger.debug("ProblemEngine çalıştırılıyor...")
        target = market_data.get("target_customer", "Users")
        
        if evidence_data["extracted_pain_points"]:
            first_pain = evidence_data["extracted_pain_points"][0]
            return f"{target} waste time or struggle with: '{first_pain}'"
            
        return "Implicit problem gap."


class OpportunityEngine(BaseEngine):
    """Sinyaldeki çözüm arayışını detaylı bir fırsat yapısına dönüştürür."""

    def analyze(self, text: str, problem_statement: str, founder_fit: Dict[str, str]) -> OpportunityIdea:
        logger.debug("OpportunityEngine çalıştırılıyor...")
        text_lower = text.lower()
        
        product_type = "Micro SaaS"
        max_pt_matches = 0
        for p_type, keywords in PRODUCT_TYPES.items():
            matches = self._count_keywords(text_lower, keywords)
            if matches > max_pt_matches:
                max_pt_matches = matches
                product_type = p_type
                
        delivery = "Web App"
        max_del_matches = 0
        for d_type, keywords in DELIVERY_METHODS.items():
            matches = self._count_keywords(text_lower, keywords)
            if matches > max_del_matches:
                max_del_matches = matches
                delivery = d_type
                
        difficulty = "Medium"
        if founder_fit.get("founder_fit_level") == FounderFitLevel.HIGH.value:
            difficulty = "Low"
        elif founder_fit.get("founder_fit_level") == FounderFitLevel.LOW.value:
            difficulty = "High"
            
        idea_statement = f"A {product_type} delivered as a {delivery} that solves the following: {problem_statement}"
        
        return OpportunityIdea(
            idea=idea_statement,
            product_type=product_type,
            delivery=delivery,
            difficulty=difficulty
        )


class WhyNowEngine(BaseEngine):
    """Zamanlama ve aciliyet faktörlerini inceler."""

    def analyze(self, text: str) -> Dict[str, Any]:
        logger.debug("WhyNowEngine çalıştırılıyor...")
        matches = self._count_keywords(text.lower(), URGENCY_KEYWORDS)
        return {
            "has_urgency_signal": matches > 0,
            "why_now_strength": "High" if matches >= 2 else ("Medium" if matches == 1 else "Low")
        }


class FounderFitEngine(BaseEngine):
    """Solo kurucular için uygunluk durumunu inceler."""

    def analyze(self, text: str) -> Dict[str, str]:
        logger.debug("FounderFitEngine çalıştırılıyor...")
        text_lower = text.lower()
        
        red_flags_count = self._count_keywords(text_lower, RED_FLAGS)
        green_flags_count = self._count_keywords(text_lower, GREEN_FLAGS)
        
        fit_level = FounderFitLevel.MEDIUM
        if green_flags_count > red_flags_count:
            fit_level = FounderFitLevel.HIGH
        elif red_flags_count > 0:
            fit_level = FounderFitLevel.LOW
            
        return {
            "founder_fit_level": fit_level.value
        }


class MetadataEngine:
    """Analiz işleminin meta verilerini üretir."""

    def analyze(self, analysis_time_ms: float) -> Dict[str, Any]:
        logger.debug("MetadataEngine çalıştırılıyor...")
        return {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": INTELLIGENCE_ENGINE_VERSION,
            "rules_version": RULES_VERSION,
            "analysis_time_ms": round(analysis_time_ms, 2)
        }


# Motorların başlatılması
_evidence_engine = EvidenceEngine()
_category_engine = CategoryEngine()
_trend_engine = TrendEngine()
_market_engine = MarketEngine()
_business_model_engine = BusinessModelEngine()
_competition_engine = CompetitionEngine()
_problem_engine = ProblemEngine()
_opportunity_engine = OpportunityEngine()
_why_now_engine = WhyNowEngine()
_founder_fit_engine = FounderFitEngine()
_metadata_engine = MetadataEngine()


def _calculate_confidence(evidence: Dict[str, Any], problem: str, opportunity: OpportunityIdea, market: Dict[str, str], category: Dict[str, str]) -> float:
    """Belirlenen ağırlıklara göre analizin genel güven seviyesini (0.0 - 1.0) hesaplar."""
    score = 0.0
    
    # 1. Evidence
    ev_score = 0.0
    if evidence.get("has_clear_pain"): ev_score += 0.5
    if evidence.get("has_workaround"): ev_score += 0.5
    score += ev_score * CONFIDENCE_WEIGHTS.get("evidence", 0.35)
    
    # 2. Problem
    if problem != "Implicit problem gap.": 
        score += CONFIDENCE_WEIGHTS.get("problem", 0.20)
        
    # 3. Opportunity
    if opportunity.idea and "Implicit problem" not in opportunity.idea: 
        score += CONFIDENCE_WEIGHTS.get("opportunity", 0.20)
        
    # 4. Market
    if market.get("market_type") != MarketType.HYBRID.value or market.get("target_customer") != "General": 
        score += CONFIDENCE_WEIGHTS.get("market", 0.15)
        
    # 5. Category
    if category.get("primary_category") != "Uncategorized": 
        score += CONFIDENCE_WEIGHTS.get("category", 0.10)
        
    return round(score, 2)


def analyze_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tek bir standardize sinyali analiz eder ve json serialize edilebilir
    intelligence verisini ekler.
    """
    logger.info(f"Sinyal analizi başlatıldı: {signal.get('id', 'Unknown ID')}")
    start_time = time.perf_counter()
    
    title = str(signal.get("title", ""))
    content = str(signal.get("content", ""))
    full_text = f"{title}. {content}"
    tags = signal.get("tags", [])
    upvotes = int(signal.get("upvotes", 0))
    comments = int(signal.get("comments", 0))

    # Temel motorlar
    evidence = _evidence_engine.analyze(full_text)
    market = _market_engine.analyze(full_text)
    category = _category_engine.analyze(full_text, tags)
    founder_fit = _founder_fit_engine.analyze(full_text)
    
    # Bağımlı motorlar
    problem = _problem_engine.analyze(evidence, market)
    opportunity_idea = _opportunity_engine.analyze(full_text, problem, founder_fit)
    
    intelligence_payload = {
        "evidence": evidence,
        "category": category,
        "trend_strength": _trend_engine.analyze(upvotes, comments),
        "market_type": market,
        "business_models": _business_model_engine.analyze(full_text),
        "competition_level": _competition_engine.analyze(full_text),
        "problem": problem,
        "opportunity": asdict(opportunity_idea), # Dataclass'ı Dict'e çeviriyoruz
        "why_now": _why_now_engine.analyze(full_text),
        "founder_fit": founder_fit
    }
    
    intelligence_payload["confidence_score"] = _calculate_confidence(
        evidence=evidence,
        problem=problem,
        opportunity=opportunity_idea,
        market=market,
        category=category
    )
    
    analysis_time_ms = (time.perf_counter() - start_time) * 1000
    intelligence_payload["analysis_metadata"] = _metadata_engine.analyze(analysis_time_ms)
    
    enriched_signal = signal.copy()
    enriched_signal["intelligence"] = intelligence_payload
    
    logger.info(f"Sinyal analizi tamamlandı: {signal.get('id', 'Unknown ID')} ({intelligence_payload['analysis_metadata']['analysis_time_ms']}ms)")
    return enriched_signal


def analyze_signals(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sinyal listesini toplu olarak analiz eder."""
    logger.info(f"Toplu analiz başlatılıyor. Sinyal Sayısı: {len(signals)}")
    return [analyze_signal(signal) for signal in signals]
