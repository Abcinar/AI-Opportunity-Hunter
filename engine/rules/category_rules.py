"""
category_rules.py

Immutable keyword-to-taxonomy mappings for the
Opportunity Intelligence Platform (OIP).

This module contains only static classification rules.
No classes, functions or business logic are permitted.
All keywords are lowercase and unique within their scope.
Categories, subcategories and keywords are alphabetically ordered.
"""

__all__ = ["CATEGORY_RULES"]

CATEGORY_RULES: dict[str, dict[str, list[str]]] = {
    ...
}
