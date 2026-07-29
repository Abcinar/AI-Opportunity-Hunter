"""
AI Opportunity Hunter - Configuration
"""

# Engine Versiyonları
INTELLIGENCE_ENGINE_VERSION = "2.1.0"
RULES_VERSION = "1.1.0"

# Trend Engine Eşik Değerleri
TREND_HIGH_ENGAGEMENT_THRESHOLD = 100
TREND_MEDIUM_ENGAGEMENT_THRESHOLD = 20

# Güven Skoru (Confidence) Ağırlıkları
CONFIDENCE_WEIGHTS = {
    "evidence": 0.35,
    "problem": 0.20,
    "opportunity": 0.20,
    "market": 0.15,
    "category": 0.10
}
