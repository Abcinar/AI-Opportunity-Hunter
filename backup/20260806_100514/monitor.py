"""
AI Opportunity Hunter - Opportunity Monitor
-------------------------------------------
Kullanıcının takip ettiği fırsatları izler,
momentum değişimi ve yeni sinyalleri takip eder.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class TrackedOpportunity:
    id: str
    title: str
    url: str
    source: str
    original_score: int
    current_score: int
    status: str = "stable"              # rising | stable | declining
    created_at: str = ""
    last_checked: str = ""
    notes: str = ""
    alerts: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.last_checked:
            self.last_checked = now


class OpportunityMonitor:
    """
    Takip edilen fırsatları yönetir.
    Veriler JSON dosyasında saklanır (MVP için yeterli).
    """

    def __init__(self, storage_path: str = "tracked_opportunities.json"):
        self.storage_path = Path(storage_path)
        self.opportunities: List[TrackedOpportunity] = []
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.opportunities = [TrackedOpportunity(**item) for item in data]
            except Exception as e:
                print(f"  Monitor yükleme hatası: {e}")
                self.opportunities = []
        else:
            self.opportunities = []

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(
                [asdict(op) for op in self.opportunities],
                f,
                ensure_ascii=False,
                indent=2,
            )

    def track(self, title: str, url: str, source: str, score: int, notes: str = "") -> TrackedOpportunity:
        """Yeni fırsat ekle."""
        opp_id = f"opp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        opp = TrackedOpportunity(
            id=opp_id,
            title=title,
            url=url,
            source=source,
            original_score=score,
            current_score=score,
            status="stable",
            notes=notes,
            history=[{"date": datetime.now().isoformat(), "score": score, "event": "tracked"}],
        )
        self.opportunities.append(opp)
        self._save()
        return opp

    def untrack(self, opp_id: str) -> bool:
        """Takibi bırak."""
        before = len(self.opportunities)
        self.opportunities = [o for o in self.opportunities if o.id != opp_id]
        if len(self.opportunities) < before:
            self._save()
            return True
        return False

    def get(self, opp_id: str) -> Optional[TrackedOpportunity]:
        for opp in self.opportunities:
            if opp.id == opp_id:
                return opp
        return None

    def list_all(self) -> List[TrackedOpportunity]:
        return self.opportunities

    def update_score(self, opp_id: str, new_score: int, event: str = "score_update") -> Optional[TrackedOpportunity]:
        """Skoru güncelle ve status hesapla."""
        opp = self.get(opp_id)
        if not opp:
            return None

        old_score = opp.current_score
        opp.current_score = new_score
        opp.last_checked = datetime.now().isoformat()

        diff = new_score - old_score
        if diff >= 5:
            opp.status = "rising"
            opp.alerts.append(f"Momentum arttı: {old_score} → {new_score}")
        elif diff <= -5:
            opp.status = "declining"
            opp.alerts.append(f"Momentum düştü: {old_score} → {new_score}")
        else:
            opp.status = "stable"

        opp.history.append({
            "date": datetime.now().isoformat(),
            "score": new_score,
            "event": event,
            "diff": diff,
        })

        opp.alerts = opp.alerts[-10:]
        opp.history = opp.history[-30:]
        self._save()
        return opp

    def add_alert(self, opp_id: str, message: str) -> bool:
        """Uyarı ekle."""
        opp = self.get(opp_id)
        if not opp:
            return False
        opp.alerts.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {message}")
        opp.alerts = opp.alerts[-10:]
        opp.last_checked = datetime.now().isoformat()
        self._save()
        return True

    def check_all(self) -> List[Dict[str, Any]]:
        """Tüm takip edilen fırsatların özet raporu."""
        return [
            {
                "id": opp.id,
                "title": opp.title[:60],
                "status": opp.status,
                "score": f"{opp.original_score} → {opp.current_score}",
                "alerts_count": len(opp.alerts),
                "last_checked": opp.last_checked[:10],
            }
            for opp in self.opportunities
        ]

    def summary(self) -> str:
        """Kısa özet metni."""
        if not self.opportunities:
            return "Henüz takip edilen fırsat yok."

        rising = sum(1 for o in self.opportunities if o.status == "rising")
        declining = sum(1 for o in self.opportunities if o.status == "declining")
        stable = sum(1 for o in self.opportunities if o.status == "stable")
        total_alerts = sum(len(o.alerts) for o in self.opportunities)

        return "\n".join([
            f"Takip edilen fırsat: {len(self.opportunities)}",
            f"  ↑ Yükselen : {rising}",
            f"  → Sabit    : {stable}",
            f"  ↓ Düşen    : {declining}",
            f"  Toplam uyarı: {total_alerts}",
        ])


if __name__ == "__main__":
    monitor = OpportunityMonitor()

    print("=" * 50)
    print("Opportunity Monitor - Demo")
    print("=" * 50)

    opp = monitor.track(
        title="AI customer support for small e-commerce stores",
        url="https://news.ycombinator.com/item?id=example",
        source="hacker_news",
        score=74,
        notes="Solo founder için uygun görünüyor",
    )
    print(f"\nTakibe alındı → {opp.id}")

    monitor.update_score(opp.id, 82, event="new_hn_discussion")
    print("Skor güncellendi: 74 → 82")

    monitor.add_alert(opp.id, "Benzer bir ürün Product Hunt'ta launch oldu")
    print("Uyarı eklendi")

    print("\n" + monitor.summary())
    print("\nDetaylı rapor:")
    for row in monitor.check_all():
        print(f"  {row}")
