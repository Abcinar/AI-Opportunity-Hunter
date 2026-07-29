"""
Opportunity Intelligence Engine V2
----------------------------------
Bu modül, Normalizer'dan gelen standartlaştırılmış sinyalleri alır ve 
yapılandırılmış içgörülere (intelligence) dönüştürür. 
Puanlama (Scoring) yapmaz; sadece analiz üretir.

İçerdiği Motorlar:
- Evidence Engine: Somut kanıtları ve acı noktalarını çıkarır.
- Category Engine: Sinyali uygun startup kategorilerine ayırır.
- Trend Engine: Pazar trendini ve momentumu analiz eder.
- Market Engine: Pazar dinamiklerini (B2B/B2C) belirler.
- Startup Engine: Solo kurucular için yapılabilirliği değerlendirir.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EvidenceEngine:
    """Metin içindeki somut kanıtları, şikayetleri ve arayışları tespit eder."""
    
    PAIN_KEYWORDS = [
        "hate", "struggle", "annoying", "tired of", "wish there was",
        "is there a tool", "how do you manage", "takes too long", "expensive",
        "nefret ediyorum", "yoruldum", "keşke", "nasıl çözüyorsunuz", "çok pahalı"
    ]
    
    SOLUTION_KEYWORDS = [
        "built this", "my solution", "wrote a script", "workaround",
        "bunu yaptım", "çözümüm", "script yazdım", "alternatif"
    ]

    def extract_evidence(self, text: str) -> Dict[str, Any]:
        """Metni analiz ederek acı noktalarını ve olası çözümleri yapılandırır."""
        text_lower = text.lower()
        
        pain_points_found = [kw for kw in self.PAIN_KEYWORDS if kw in text_lower]
        solutions_found = [kw for kw in self.SOLUTION_KEYWORDS if kw in text_lower]
        
        has_clear_pain = len(pain_points_found) > 0
        has_workaround = len(solutions_found) > 0
        
        evidence_score_base = (len(pain_points_found) * 0.5) + (len(solutions_found) * 0.5)
        
        return {
            "has_clear_pain": has_clear_pain,
            "has_workaround": has_workaround,
            "pain_keywords_detected": pain_points_found,
            "solution_keywords_detected": solutions_found,
            "evidence_strength": min(1.0, evidence_score_base) # 0.0 ile 1.0 arası normalize
        }


class CategoryEngine:
    """Sinyalleri bilinen mikro-startup kategorilerine sınıflandırır."""
    
    CATEGORIES = {
        "DevTools": ["api", "developer", "deploy", "cli", "github", "react", "backend", "framework"],
        "SaaS": ["subscription", "mrr", "dashboard", "b2b", "saas", "platform", "tenant"],
        "AI/ML": ["openai", "llm", "chatgpt", "machine learning", "ai", "prompt", "generator"],
        "Productivity": ["notion", "todo", "calendar", "notes", "workflow", "automate"],
        "Creator Economy": ["newsletter", "youtube", "audience", "monetize", "patreon", "gumroad"],
        "Marketing": ["seo", "ads", "conversion", "landing page", "leads", "email marketing"]
    }

    def determine_categories(self, text: str, tags: List[str]) -> List[str]:
        """İçerik ve etiketlere bakarak sinyalin kategorilerini belirler."""
        matched_categories = set()
        text_lower = text.lower()
        combined_tags = [tag.lower() for tag in tags]

        for category, keywords in self.CATEGORIES.items():
            # Metin içi kontrol
            if any(kw in text_lower for kw in keywords):
                matched_categories.add(category)
            # Tag kontrol
            if any(kw in combined_tags for kw in keywords):
                matched_categories.add(category)
                
        if not matched_categories:
            matched_categories.add("Uncategorized")
            
        return list(matched_categories)


class TrendEngine:
    """Sinyalin momentumunu ve popülaritesini analiz eder."""
    
    def analyze_momentum(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Upvote, yorum sayısı ve zamana bağlı ivmeyi hesaplar."""
        upvotes = signal.get("upvotes", 0)
        comments = signal.get("comments", 0)
        created_at = signal.get("created_at") # ISO 8601 string beklenir
        
        # Basit bir age-penalty algoritması
        age_in_hours = 24 
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_in_hours = max(1, (now - created_date).total_seconds() / 3600)
            except ValueError:
                logger.warning(f"Tarih formatı ayrıştırılamadı: {created_at}")

        # Hacker News tarzı momentum hesaplama: (Upvotes + Comments) / Age^1.5
        velocity = (upvotes + (comments * 2)) / (age_in_hours ** 1.5)
        
        is_viral = velocity > 5.0  # Threshold değeri
        
        return {
            "velocity": round(velocity, 4),
            "age_in_hours": round(age_in_hours, 2),
            "is_viral": is_viral,
            "engagement_ratio": round(comments / max(1, upvotes), 2)
        }


class MarketEngine:
    """Pazar türünü (B2B/B2C) ve muhtemel ödeme gücünü (Willingness to Pay) analiz eder."""
    
    B2B_KEYWORDS = ["enterprise", "team", "b2b", "agency", "client", "business", "company", "employee"]
    B2C_KEYWORDS = ["personal", "b2c", "individual", "hobby", "family", "student", "myself"]
    
    def analyze_market(self, text: str) -> Dict[str, Any]:
        """Metinden yola çıkarak pazar analizini gerçekleştirir."""
        text_lower = text.lower()
        
        b2b_score = sum(1 for kw in self.B2B_KEYWORDS if kw in text_lower)
        b2c_score = sum(1 for kw in self.B2C_KEYWORDS if kw in text_lower)
        
        target_audience = "B2B" if b2b_score > b2c_score else "B2C"
        if b2b_score == b2c_score:
            target_audience = "Hybrid/Unknown"
            
        # Basit "Ödeme İsteği" (Willingness to pay) analizi
        wtp_keywords = ["pay for", "buy", "subscribe", "expensive", "cost", "pricing"]
        willingness_to_pay = any(kw in text_lower for kw in wtp_keywords)
        
        return {
            "target_audience": target_audience,
            "willingness_to_pay_signal": willingness_to_pay,
            "market_clarity_score": b2b_score + b2c_score # Pazarın ne kadar net ifade edildiği
        }


class StartupEngine:
    """Solo founder'lar ve Indie Hacker'lar için uygunluk analizi."""
    
    COMPLEXITY_FLAGS = ["hardware", "legal", "compliance", "medical", "enterprise sales", "blockchain", "web3"]
    
    def evaluate_solo_feasibility(self, text: str, categories: List[str]) -> Dict[str, Any]:
        """Projenin tek kişi tarafından yapılıp yapılamayacağını öngörür."""
        text_lower = text.lower()
        
        # Kompleksite cezaları
        complexity_hits = [flag for flag in self.COMPLEXITY_FLAGS if flag in text_lower]
        
        # Avantajlar (SaaS ve DevTools solo için genellikle daha uygundur)
        is_indie_friendly = "SaaS" in categories or "DevTools" in categories or "Productivity" in categories
        
        solo_feasibility_score = 1.0 # Başlangıç mükemmel
        
        if complexity_hits:
            solo_feasibility_score -= (len(complexity_hits) * 0.3)
            
        if not is_indie_friendly:
            solo_feasibility_score -= 0.2
            
        solo_feasibility_score = max(0.0, min(1.0, solo_feasibility_score))
        
        return {
            "is_solo_friendly": solo_feasibility_score > 0.6,
            "solo_feasibility_score": round(solo_feasibility_score, 2),
            "complexity_warnings": complexity_hits
        }


# Global Engine Örneklemeleri (Tekrar tekrar initialize etmemek için)
evidence_engine = EvidenceEngine()
category_engine = CategoryEngine()
trend_engine = TrendEngine()
market_engine = MarketEngine()
startup_engine = StartupEngine()


def analyze_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tek bir normalize edilmiş sinyali alır ve Intelligence katmanından geçirir.
    
    Args:
        signal (dict): Normalizer'dan çıkan standart sözlük yapısı.
                       Beklenen anahtarlar: id, title, content, url, source, upvotes, comments, created_at, tags
                       
    Returns:
        dict: Zenginleştirilmiş zeka verisini içeren dictionary.
    """
    try:
        # 1. Metin hazırlığı (Title ve Content birleştirilir)
        title = signal.get("title", "")
        content = signal.get("content", "")
        full_text = f"{title}. {content}"
        tags = signal.get("tags", [])
        
        # 2. Engine Çalıştırmaları
        evidence_data = evidence_engine.extract_evidence(full_text)
        categories = category_engine.determine_categories(full_text, tags)
        trend_data = trend_engine.analyze_momentum(signal)
        market_data = market_engine.analyze_market(full_text)
        startup_data = startup_engine.evaluate_solo_feasibility(full_text, categories)
        
        # 3. Zenginleştirilmiş veriyi derleme (Single Source of Truth yapısına uygun)
        enriched_signal = signal.copy()
        
        enriched_signal["intelligence"] = {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "evidence": evidence_data,
            "categories": categories,
            "trend": trend_data,
            "market": market_data,
            "startup_feasibility": startup_data
        }
        
        logger.debug(f"Signal {signal.get('id')} başarıyla analiz edildi.")
        return enriched_signal
        
    except Exception as e:
        logger.error(f"Sinyal analizinde hata (ID: {signal.get('id')}): {str(e)}")
        # Hata durumunda sinyalin orjinalini bozmadan geri dön, logla.
        signal["intelligence_error"] = str(e)
        return signal


def analyze_signals(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Birden fazla sinyali toplu halde analiz eder.
    
    Args:
        signals (list): Normalize edilmiş sinyal sözlükleri listesi.
        
    Returns:
        list: İçgörü (intelligence) verisi eklenmiş sinyal listesi.
    """
    logger.info(f"Toplam {len(signals)} sinyal için Intelligence Engine başlatılıyor...")
    
    analyzed_signals = []
    for signal in signals:
        result = analyze_signal(signal)
        analyzed_signals.append(result)
        
    logger.info("Intelligence analizi tamamlandı.")
    return analyzed_signals


if __name__ == "__main__":
    # Geliştirme ve test aşaması için küçük bir mock veri simülasyonu
    test_signals = [
        {
            "id": "hn_12345",
            "title": "Ask HN: Is there a tool for managing multiple AWS accounts easily?",
            "content": "I hate having to switch roles all the time. It takes too long and is really annoying. I wish there was a simple dashboard.",
            "url": "https://news.ycombinator.com/item?id=12345",
            "source": "Hacker News",
            "upvotes": 120,
            "comments": 45,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": ["aws", "devops"]
        }
    ]
    
    results = analyze_signals(test_signals)
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))
