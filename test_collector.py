from engine.collector import collect_all_sources

signals = collect_all_sources()

print()

print("Toplam:", signals["total_signals"])

print(signals["sources"])
