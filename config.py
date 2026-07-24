"""
AI Opportunity Hunter Configuration
"""

from pathlib import Path 

DATA_DIR = Path("data")

DAILY_SIGNALS_FILE = DATA_DIR / "daily_signals.json"
OPPORTUNITIES_FILE = DATA_DIR / "opportunities.json"
TRACKED_FILE = DATA_DIR / "tracked_opportunities.json"

# Proje dizini
BASE_DIR = Path(__file__).resolve().parent

# Veri klasörü
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# JSON dosyaları
DAILY_SIGNALS_FILE = DATA_DIR / "daily_signals.json"
TRACKED_FILE = DATA_DIR / "tracked_opportunities.json"

# Fetch ayarları
GITHUB_LIMIT = 10
HN_LIMIT = 10
GOOGLE_LIMIT = 10
PRODUCTHUNT_LIMIT = 10
BETALIST_LIMIT = 10
