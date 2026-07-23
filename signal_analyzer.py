"""
AI Opportunity Hunter - Signal Analyzer
---------------------------------------
Ham post verisinden Opportunity Score için
gerçekçi SignalInput üretir + fırsat filtresi.
"""

import re
from typing import Dict, Any
from scoring import SignalInput


# ------------------------------------------------------------
# Anahtar kelime listeleri
# ------------------------------------------------------------

PAIN_KEYWORDS = [
    "problem", "hate", "frustrated", "annoying", "expensive", "slow",
    "broken", "sucks", "pain", "struggle", "difficult", "hard to",
    "wish there was", "looking for", "need a", "alternative to",
    "sorun", "pahalı", "yavaş", "kötü", "çalışmıyor",
]

COMPETITION_KEYWORDS = [
    "alternative", "vs", "versus", "better than", "instead of",
    "open source", "self-hosted", "competitor", "compared to",
]

FEASIBILITY_POSITIVE = [
    "simple", "easy", "no-code", "low-code", "api", "script",
    "weekend project", "side project", "mvp", "lightweight",
    "basit", "kolay", "i built", "i made", "i launched",
]

FEASIBILITY_NEGATIVE = [
    "enterprise", "complex", "infrastructure", "hardware",
    "regulated", "compliance", "machine learning research",
    "deep learning", "requires team",
]

MONETIZATION_KEYWORDS = [
    "paid", "pricing", "subscription", "revenue", "monetize",
    "saas", "price", "billing", "pay", "customer", "business model",
    "ücretli", "fiyat", "abonelik",
]

# Fırsat sinyali veren kalıplar
OPPORTUNITY_PATTERNS = [
    r"show hn",
    r"ask hn",
    r"i built",
    r"i made
