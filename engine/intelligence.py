"""
Opportunity Intelligence Engine V2 (Refined)
--------------------------------------------
AI Opportunity Hunter projesinin analiz katmanı.
Sinyalleri alır, anlamlandırır ve yapılandırılmış zeka (intelligence) üretir.
Tamamen Rule-Based V1 mimarisiyle çalışır. LLM veya harici API içermez.

En Önemli Kural: Single Source of Truth (opportunities.json)
Bu modül puan, karar veya öneri (recommendation) üretmez; yalnızca analiz eder.
"""

import re
import time
from datetime import datetime, timezone
from typing import Any


class BaseEngine:
    """Tüm motorlar için temel yardımcı fonksiyonları barındıran üst sınıf."""
    
    @staticmethod
    def _count_keywords(text: str, keywords: list[str]) -> int:
        """Metin içindeki anahtar kelime eşleşme sayısını döndürür."""
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower)
    
    @staticmethod
    def _extract_sentences(text: str, keywords: list[str]) -> list[str]:
        """Belirli anahtar kelimeleri içeren cümleleri çıkarır."""
        sentences = re.split(r'(?<=[.!?]) +', text)
        matched = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in keywords):
                matched.append(sentence.strip())
        return matched

    @staticmethod
    def _find_matched_keywords(text: str, keywords: list[str]) -> list[str]:
        """Metinde eşleşen spesifik anahtar kelimeleri döndürür."""
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower]


class EvidenceEngine(BaseEngine):
    """Sinyal içindeki somut kanıtları (acı noktaları, şikayetler, çözümler) tespit eder."""
    
    PAIN_KEYWORDS = [
        "hate", "struggle", "annoying", "tired of", "wish there was",
        "is there a tool", "how do you manage", "takes too long", "expensive",
        "hard to", "sucks", "frustrating", "issue", "problem"
    ]
    
    SOLUTION_KEYWORDS = [
        "built this", "my solution", "wrote a script", "workaround",
        "alternative to", "open source alternative", "fixed it by"
    ]

    def analyze(self, text: str) -> dict[str, Any]:
        """Kanıt analizini çalıştırır."""
        pain_points = self._extract_sentences(text, self.PAIN_KEYWORDS)
        solutions = self._extract_sentences(text, self.SOLUTION_KEYWORDS)
        
        return {
            "has_clear_pain": len(pain_points) > 0,
            "has_workaround": len(solutions) > 0,
            "extracted_pain_points": pain_points,
            "extracted_solutions": solutions,
            "evidence_count": len(pain_points) + len(solutions)
        }


class CategoryEngine(BaseEngine):
    """Sinyali ana kategoriye ve alt kategoriye ayırır."""
    
    CATEGORIES = {
        "DevTools": ["api", "developer", "deploy", "cli", "github", "react", "backend", "framework", "aws", "docker"],
        "SaaS": ["subscription", "mrr", "dashboard", "b2b", "saas", "platform", "tenant"],
        "AI/ML": ["openai", "llm", "chatgpt", "machine learning", "ai", "prompt", "generator", "huggingface"],
        "Productivity": ["notion", "todo", "calendar", "notes", "workflow", "automate", "efficiency"],
        "Creator Economy": ["newsletter", "youtube", "audience", "monetize", "patreon", "gumroad", "creator"],
        "Marketing": ["seo", "ads", "conversion", "landing page", "leads", "email marketing", "analytics"]
    }
    
    SUB_CATEGORIES = {
        "Infrastructure": ["aws", "docker", "kubernetes", "hosting"],
        "Content Generation": ["generator", "prompt", "write", "copywriting"],
        "Task Management": ["todo", "kanban", "calendar", "tracker"],
        "Data Analytics": ["analytics", "metrics", "dashboard", "tracking"]
    }

    def analyze(self, text: str, tags: list[str]) -> dict[str, str]:
        """Kategori analizini çalıştırır."""
        combined_text = f"{text} {' '.join(tags)}".lower()
        
        primary_category = "Uncategorized"
        max_matches = 0
        
        for cat, keywords in self.CATEGORIES.items():
            matches = self._count_keywords(combined_text, keywords)
            if matches > max_matches:
                max_matches = matches
                primary_category = cat
                
        sub_category = "General"
        max_sub_matches = 0
        
        for sub, keywords in self.SUB_CATEGORIES.items():
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
    
    HIGH_ENGAGEMENT_THRESHOLD = 100
    MEDIUM_ENGAGEMENT_THRESHOLD = 20

    def analyze(self, upvotes: int, comments: int) -> dict[str, str]:
        """Trend gücünü analiz eder."""
        total_engagement = upvotes + (comments * 2)
        
        if total_engagement >= self.HIGH_ENGAGEMENT_THRESHOLD:
            trend_strength = "Strong"
        elif total_engagement >= self.MEDIUM_ENGAGEMENT_THRESHOLD:
            trend_strength = "Moderate"
        else:
            trend_strength = "Weak"
            
        return {
            "trend_strength": trend_strength,
            "engagement_tier": trend_strength
        }


class MarketEngine(BaseEngine):
    """Pazar tipini (B2B/B2C) ve hedef kitleyi analiz eder."""
    
    B2B_KEYWORDS = ["enterprise", "team", "b2b", "agency", "client", "business", "company", "employee", "startup", "founder"]
    B2C_KEYWORDS = ["personal", "b2c", "individual", "hobby", "family", "student", "myself", "consumer"]
    
    TARGET_CUSTOMERS = {
        "Developers": ["developer", "engineer", "programmer", "coder", "devops", "aws"],
        "Designers": ["designer", "ui", "ux", "figma"],
        "Marketers": ["marketer", "seo", "agency", "sales"],
        "Founders": ["founder", "startup", "entrepreneur", "indie hacker"]
    }
    
    MARKET_SIZE_INDICATORS = {
        "Niche": ["niche", "specific", "specialized", "small team"],
        "Large": ["enterprise", "global", "millions", "everyone", "massive"]
    }

    def analyze(self, text: str) -> dict[str, str]:
        """Pazar analizini çalıştırır."""
        text_lower = text.lower()
        
        b2b_score = self._count_keywords(text_lower, self.B2B_KEYWORDS)
        b2c_score = self._count_keywords(text_lower, self.B2C_KEYWORDS)
        
        market_type = "Hybrid"
        if b2b_score > b2c_score:
            market_type = "B2B"
        elif b2c_score > b2b_score:
            market_type = "B2C"
            
        target_customer = "General"
        max_target_matches = 0
        for audience, keywords in self.TARGET_CUSTOMERS.items():
            matches = self._count_keywords(text_lower, keywords)
            if matches > max_target_matches:
                max_target_matches = matches
                target_customer = audience
                
        market_size = "Medium"
        niche_score = self._count_keywords(text_lower, self.MARKET_SIZE_INDICATORS["Niche"])
        large_score = self._count_keywords(text_lower, self.MARKET_SIZE_INDICATORS["Large"])
        
        if niche_score > large_score:
            market_size = "Niche"
        elif large_score > niche_score:
            market_size = "Large"
            
        return {
            "market_type": market_type,
            "target_customer": target_customer,
            "market_size": market_size
        }


class BusinessModelEngine(BaseEngine):
    """Uygun iş modellerini ağırlıklı olarak tahmin eder."""
    
    MODELS = {
        "SaaS": ["subscription", "mrr", "monthly", "saas", "tier", "recurring", "monthly fee"],
        "API": ["api", "endpoint", "webhook", "token", "developer access", "request limit"],
        "Freemium": ["free tier", "freemium", "community edition", "upgrade for", "premium features"],
        "Enterprise": ["enterprise", "custom SLA", "contact sales", "security compliance", "sso"],
        "Marketplace": ["marketplace", "platform", "connect buyers", "commission", "fee per transaction"],
        "White Label": ["white label", "reseller", "custom branding", "agency plan"]
    }

    def analyze(self, text: str) -> dict[str, float]:
        """İş modeli analizini çalıştırarak her model için bir güven skoru üretir."""
        model_scores = {}
        text_lower = text.lower()
        
        total_keywords_found = 0
        raw_scores = {}
        
        for model, keywords in self.MODELS.items():
            matches = self._count_keywords(text_lower, keywords)
            raw_scores[model] = matches
            total_keywords_found += matches
            
        if total_keywords_found == 0:
            return {"SaaS": 0.5, "Undetermined": 1.0} # Default assumption with indicator
            
        for model, score in raw_scores.items():
            if score > 0:
                # 0.0 - 1.0 aralığına normalize et ve ağırlıklandır
                confidence = min(1.0, (score / total_keywords_found) + (score * 0.1))
                model_scores[model] = round(confidence, 2)
                
        return dict(sorted(model_scores.items(), key=lambda item: item[1], reverse=True))


class CompetitionEngine(BaseEngine):
    """Rekabet düzeyini ve nedenlerini analiz eder."""
    
    HIGH_COMPETITION_KEYWORDS = ["alternative to", "better than", "vs", "competitor", "crowded", "saturated", "clone"]
    LOW_COMPETITION_KEYWORDS = ["first of its kind", "no tools for", "couldn't find", "nothing exists", "untapped"]

    def analyze(self, text: str) -> dict[str, Any]:
        """Rekabet seviyesini ve belirleyici anahtar kelimeleri döndürür."""
        text_lower = text.lower()
        
        high_matched = self._find_matched_keywords(text_lower, self.HIGH_COMPETITION_KEYWORDS)
        low_matched = self._find_matched_keywords(text_lower, self.LOW_COMPETITION_KEYWORDS)
        
        high_score = len(high_matched)
        low_score = len(low_matched)
        
        competition_level = "Medium"
        reason = "No strong competition indicators found."
        matched_keywords = []
        
        if high_score > low_score:
            competition_level = "High"
            reason = "Mentions direct competitors or alternative solutions."
            matched_keywords = high_matched
        elif low_score > high_score:
            competition_level = "Low"
            reason = "Indicates a lack of existing solutions or tools."
            matched_keywords = low_matched
            
        return {
            "competition_level": competition_level,
            "reason": reason,
            "matched_keywords": matched_keywords
        }


class ProblemEngine(BaseEngine):
    """Sinyalin işaret ettiği temel problemi, hedef kitle ile birleştirerek özetler."""

    def analyze(self, evidence_data: dict[str, Any], market_data: dict[str, str]) -> str:
        """Problem tanımını analiz eder ve yapılandırır."""
        target = market_data.get("target_customer", "Users")
        
        if evidence_data["extracted_pain_points"]:
            # İlk acı noktasını al ve temizle
            first_pain = evidence_data["extracted_pain_points"][0]
            # Basit bir kural tabanlı özet oluştur (LLM kullanmadan)
            return f"{target} waste time or struggle with: '{first_pain}'"
            
        return "Implicit problem gap."


class OpportunityEngine(BaseEngine):
    """Sinyaldeki çözüm arayışını detaylı bir fırsat yapısına dönüştürür."""
    
    PRODUCT_TYPES = {
        "Micro SaaS": ["dashboard", "tool", "monthly", "simple", "manager"],
        "API Service": ["api", "endpoint", "developer tool", "integrate"],
        "Browser Extension": ["chrome", "extension", "plugin", "browser"],
        "Automation Script": ["automate", "zapier", "script", "workflow", "sync"]
    }
    
    DELIVERY_METHODS = {
        "Web App": ["dashboard", "website", "platform", "saas"],
        "CLI Tool": ["cli", "terminal", "command line"],
        "Integration": ["zapier", "slack", "discord bot", "github action"]
    }

    def analyze(self, text: str, problem_statement: str, founder_fit: dict[str, str]) -> dict[str, str]:
        """Fırsatın ürün tipini, teslimat yöntemini ve fikrini belirler."""
        text_lower = text.lower()
        
        # Ürün Tipi Belirleme
        product_type = "Micro SaaS" # Default fallback
        max_pt_matches = 0
        for p_type, keywords in self.PRODUCT_TYPES.items():
            matches = self._count_keywords(text_lower, keywords)
            if matches > max_pt_matches:
                max_pt_matches = matches
                product_type = p_type
                
        # Teslimat Yöntemi Belirleme
        delivery = "Web App" # Default fallback
        max_del_matches = 0
        for d_type, keywords in self.DELIVERY_METHODS.items():
            matches = self._count_keywords(text_lower, keywords)
            if matches > max_del_matches:
                max_del_matches = matches
                delivery = d_type
                
        # Zorluk Derecesi Belirleme (Founder Fit verisiyle entegre)
        difficulty = "Medium"
        if founder_fit.get("founder_fit_level") == "High":
            difficulty = "Low"
        elif founder_fit.get("founder_fit_level") == "Low":
            difficulty = "High"
            
        # Fikir Cümlesi Üretimi
        idea_statement = f"A {product_type} delivered as a {delivery} that solves the following: {problem_statement}"
        
        return {
            "idea": idea_statement,
            "product_type": product_type,
            "delivery": delivery,
            "difficulty": difficulty
        }


class WhyNowEngine(BaseEngine):
    """Zamanlama ve aciliyet faktörlerini inceler."""
    
    URGENCY_KEYWORDS = ["just released", "new update", "now possible", "recent changes", "trending now", "rapidly growing", "api update"]

    def analyze(self, text: str) -> dict[str, Any]:
        """Zamanlama nedenlerini analiz eder."""
        matches = self._count_keywords(text.lower(), self.URGENCY_KEYWORDS)
        return {
            "has_urgency_signal": matches > 0,
            "why_now_strength": "High" if matches >= 2 else ("Medium" if matches == 1 else "Low")
        }


class FounderFitEngine(BaseEngine):
    """Solo kurucular için uygunluk durumunu inceler."""
    
    RED_FLAGS = ["hardware", "legal", "compliance", "medical", "enterprise sales", "blockchain", "web3", "heavy capital", "factory"]
    GREEN_FLAGS = ["api wrapper", "micro saas", "extension", "plugin", "template", "script", "no-code"]

    def analyze(self, text: str) -> dict[str, str]:
        """Kurucu uyumunu (Solo Founder fit) analiz eder."""
        text_lower = text.lower()
        
        red_flags_count = self._count_keywords(text_lower, self.RED_FLAGS)
        green_flags_count = self._count_keywords(text_lower, self.GREEN_FLAGS)
        
        fit_level = "Medium"
        if green_flags_count > red_flags_count:
            fit_level = "High"
        elif red_flags_count > 0:
            fit_level = "Low"
            
        return {
            "founder_fit_level": fit_level
        }


class MetadataEngine:
    """Analiz işleminin meta verilerini üretir."""
    
    ENGINE_VERSION = "2.1.0"
    RULES_VERSION = "1.1.0"

    def analyze(self, analysis_time_ms: float) -> dict[str, Any]:
        """Meta verileri oluşturur."""
        return {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": self.ENGINE_VERSION,
            "rules_version": self.RULES_VERSION,
            "analysis_time_ms": round(analysis_time_ms, 2)
        }


# Motorların modül seviyesinde başlatılması
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


def _calculate_confidence(evidence: dict[str, Any], problem: str, opportunity: dict[str, str], market: dict[str, str], category: dict[str, str]) -> float:
    """
    Analizin genel güven seviyesini ağırlıklı olarak hesaplar.
    Sonuç 0.0 ile 1.0 arasında bir değer döner.
    Ağırlıklar: Evidence %35, Problem %20, Opportunity %20, Market %15, Category %10.
    """
    score = 0.0
    
    # 1. Evidence (%35)
    ev_score = 0.0
    if evidence.get("has_clear_pain"): ev_score += 0.5
    if evidence.get("has_workaround"): ev_score += 0.5
    score += ev_score * 0.35
    
    # 2. Problem (%20)
    if problem != "Implicit problem gap.": 
        score += 0.20
        
    # 3. Opportunity (%20)
    if opportunity.get("product_type") and opportunity.get("product_type") != "Unknown": 
        score += 0.20
        
    # 4. Market (%15)
    if market.get("market_type") != "Hybrid" or market.get("target_customer") != "General": 
        score += 0.15
        
    # 5. Category (%10)
    if category.get("primary_category") != "Uncategorized": 
        score += 0.10
        
    return round(score, 2)


def analyze_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """
    Tek bir standardize sinyali analiz eder ve intelligence verisini ekler.
    
    Args:
        signal (dict): Normalizer katmanından gelen ham sinyal sözlüğü.
                       
    Returns:
        dict: 'intelligence' anahtarı eklenmiş, zenginleştirilmiş sinyal.
    """
    start_time = time.perf_counter()
    
    title = str(signal.get("title", ""))
    content = str(signal.get("content", ""))
    full_text = f"{title}. {content}"
    tags = signal.get("tags", [])
    upvotes = int(signal.get("upvotes", 0))
    comments = int(signal.get("comments", 0))

    evidence = _evidence_engine.analyze(full_text)
    market = _market_engine.analyze(full_text)
    category = _category_engine.analyze(full_text, tags)
    founder_fit = _founder_fit_engine.analyze(full_text)
    
    problem = _problem_engine.analyze(evidence, market)
    opportunity = _opportunity_engine.analyze(full_text, problem, founder_fit)
    
    intelligence_payload = {
        "evidence": evidence,
        "category": category,
        "trend_strength": _trend_engine.analyze(upvotes, comments),
        "market_type": market,
        "business_models": _business_model_engine.analyze(full_text),
        "competition_level": _competition_engine.analyze(full_text),
        "problem": problem,
        "opportunity": opportunity,
        "why_now": _why_now_engine.analyze(full_text),
        "founder_fit": founder_fit
    }
    
    intelligence_payload["confidence_score"] = _calculate_confidence(
        evidence=evidence,
        problem=problem,
        opportunity=opportunity,
        market=market,
        category=category
    )
    
    analysis_time_ms = (time.perf_counter() - start_time) * 1000
    intelligence_payload["analysis_metadata"] = _metadata_engine.analyze(analysis_time_ms)
    
    enriched_signal = signal.copy()
    enriched_signal["intelligence"] = intelligence_payload
    
    return enriched_signal


def analyze_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sinyal listesini toplu olarak analiz eder.
    
    Args:
        signals (list): Normalizer'dan gelen sinyaller listesi.
        
    Returns:
        list: İçgörü (intelligence) eklenmiş sinyal listesi.
    """
    return [analyze_signal(signal) for signal in signals]
