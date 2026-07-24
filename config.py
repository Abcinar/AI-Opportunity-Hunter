"""
AI Opportunity Hunter Configuration
"""

from pathlib import Path

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DAILY_SIGNALS_FILE = DATA_DIR / "daily_signals.json"
OPPORTUNITIES_FILE = DATA_DIR / "opportunities.json"
TRACKED_FILE = DATA_DIR / "tracked_opportunities.json"

# --------------------------------------------------
# Fetch Limits
# --------------------------------------------------

GITHUB_LIMIT = 10
HN_LIMIT = 10
GOOGLE_LIMIT = 10
PRODUCTHUNT_LIMIT = 10
BETALIST_LIMIT = 10
