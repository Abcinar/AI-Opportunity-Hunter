"""
AI Opportunity Hunter
Main Entry
"""

from engine.collector import collect_all_sources
from engine.exporter import save_daily_signals


def main():

    print("=" * 60)
    print("AI Opportunity Hunter")
    print("=" * 60)

    signals = collect_all_sources()

    save_daily_signals(signals)

    print()

    print(f"Toplam sinyal : {signals['total_signals']}")

    print()

    for source, count in signals["sources"].items():
        print(f"{source:20} : {count}")

    print()

    print("daily_signals.json oluşturuldu.")

    print("=" * 60)


if __name__ == "__main__":
    main()
