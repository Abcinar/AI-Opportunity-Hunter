from engine.collector import collect_all_sources
from engine.exporter import (
    save_daily_signals,
    load_daily_signals,
)

signals = collect_all_sources()

save_daily_signals(signals)

loaded = load_daily_signals()

print()

print("Toplam:", loaded["total_signals"])

print(loaded["sources"])
