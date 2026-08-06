"""
Opportunity Intelligence Platform - Data Models & Enums
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

class TrendStrength(str, Enum):
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"

class MarketType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    HYBRID = "Hybrid"

class CompetitionLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class FounderFitLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

@dataclass
class OpportunityIdea:
    idea: str
    product_type: str
    delivery: str
    difficulty: str

@dataclass
class IntelligenceData:
    evidence: Dict[str, Any]
    category: Dict[str, str]
    trend_strength: TrendStrength
    market_type: Dict[str, str]
    business_models: Dict[str, float]
    competition_level: Dict[str, Any]
    problem: str
    opportunity: OpportunityIdea
    why_now: Dict[str, Any]
    founder_fit: Dict[str, str]
    confidence_score: float
    analysis_metadata: Dict[str, Any]
