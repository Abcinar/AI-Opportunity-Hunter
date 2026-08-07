"""
Opportunity Intelligence Platform (OIP)

Public API for the Intelligence package.
"""

from .pipeline import analyze_signal, analyze_signals

__all__ = [
    "analyze_signal",
    "analyze_signals",
]
