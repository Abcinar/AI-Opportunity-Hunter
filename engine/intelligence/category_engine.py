"""
category_engine.py

Working Category Engine v1 for the Opportunity Intelligence Platform (OIP).

Responsibilities
----------------
- Receive an Opportunity (object or dict)
- Extract and normalize textual fields
- Match against CATEGORY_RULES
- Select the strongest category / subcategory deterministically
- Generate tags from matched keywords only
- Enrich and return the Opportunity

No scoring, confidence, founder-fit or recommendation logic.
"""

from __future__ import annotations

from typing import Any

from .base_engine import BaseEngine
from .constants import UNKNOWN_CATEGORY, UNKNOWN_SUBCATEGORY
from .helpers import normalize_text, set_field
from ..rules.category_rules import CATEGORY_RULES


class CategoryEngine(BaseEngine):
    """
    Classification engine that applies CATEGORY_RULES to an Opportunity.
    """

    def process(self, opportunity: Any) -> Any:
        """
        Classify the opportunity and enrich it with category,
        subcategory and tags.

        Supports both attribute-style objects and plain dictionaries.
        """
        text = normalize_text(opportunity)
        category, subcategory, tags = self._match(text)

        set_field(opportunity, "category", category)
        set_field(opportunity, "subcategory", subcategory)
        set_field(opportunity, "tags", tags)

        return opportunity

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _match(self, text: str) -> tuple[str, str, list[str]]:
        """
        Match normalized text against CATEGORY_RULES.

        Returns
        -------
        (category, subcategory, tags)
        """
        if not text.strip():
            return UNKNOWN_CATEGORY, UNKNOWN_SUBCATEGORY, []

        best_category = UNKNOWN_CATEGORY
        best_subcategory = UNKNOWN_SUBCATEGORY
        best_score = 0
        matched_keywords: set[str] = set()

        # Iterate in sorted order for deterministic tie-breaking
        for category in sorted(CATEGORY_RULES.keys()):
            subcategories = CATEGORY_RULES[category]
            for subcategory in sorted(subcategories.keys()):
                keywords = subcategories[subcategory]
                score = 0
                local_matches: set[str] = set()

                for keyword in keywords:
                    # Simple whole-word-ish presence check (case already lower)
                    if keyword in text:
                        score += 1
                        local_matches.add(keyword)

                if score > best_score:
                    best_score = score
                    best_category = category
                    best_subcategory = subcategory
                    matched_keywords = local_matches
                elif score == best_score and score > 0:
                    # Deterministic tie-break: prefer lexicographically smaller
                    # category then subcategory
                    if (category, subcategory) < (best_category, best_subcategory):
                        best_category = category
                        best_subcategory = subcategory
                        matched_keywords = local_matches

        if best_score == 0:
            return UNKNOWN_CATEGORY, UNKNOWN_SUBCATEGORY, []

        tags = sorted(matched_keywords)
        return best_category, best_subcategory, tags
