"""
AI Opportunity Hunter - Streamlit Dashboard
Calistir: streamlit run dashboard.py
"""

import json
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# Sayfa ayari
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Opportunity Hunter",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 AI Opportunity Hunter")
st.caption("Solo Founder Fırsat Karar Motoru — Günlük Dashboard")

# ------------------------------------------------------------
# Veri yukleme
# ------------------------------------------------------------
def load_json(path: str) -> dict | list:
    p = Path(path)
    if not p.exists():
        return {} if "signals" in path or path.endswith(".json") else []
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {} if "tracked" not in path else []


signals_data = load_json("daily_signals.json")
tracked_data = load_json("tracked_opportunities.json")
if isinstance(tracked_data, dict):
    tracked_data = tracked_data.get("opportunities", [])

posts = signals_data.get("posts", []) if isinstance(signals_data, dict) else []
sources = signals_data.get("sources", {}) if isinstance(signals_data, dict) else {}
fetched_at = signals_data.get("fetched_at", "—") if isinstance(signals_data, dict) else "—"

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
with st.sidebar:
    st.header("Kontrol")
    st.write(f"**Son çekim:** {fetched_at[:19] if fetched_at != '—' else '—'}")
    st.write(f"**Toplam sinyal:** {len(posts)}")
    st.write(f"**Takip edilen:** {len(tracked_data) if isinstance(tracked_data, list) else 0}")
    st.divider()
    top_n = st.slider("Gösterilecek fırsat sayısı", 3, 15, 5)
    min_points = st.number_input("Min. etkileşim (puan)", 0, 5000, 0, 10)
    st.divider()
    st.markdown("Terminalden veri yenilemek için:")
    st.code("python main.py", language="bash")

# ------------------------------------------------------------
# Ust metrikler
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Toplam Sinyal", len(posts))
col2.metric("Kaynak Sayısı", len([k for k, v in sources.items() if v > 0]))
col3.metric("Takip Listesi", len(tracked_data) if isinstance(tracked_data, list) else 0)
col4.metric("Filtrelenebilir", sum(1 for p in posts if (p.get("points") or 0) >= min_points))

st.divider()

# ------------------------------------------------------------
# Kaynak dagilimi
# ------------------------------------------------------------
st.subheader("📡 Kaynak Dağılımı")

if sources:
    src_df = pd.DataFrame(
        [{"Kaynak": k, "Sinyal": v} for k, v in sources.items() if v > 0]
    )
    if not src_df.empty:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(src_df, hide_index=True, use_container_width=True)
        with c2:
            st.bar_chart(src_df.set_index("Kaynak"))
    else:
        st.info("Kaynak verisi yok. Önce `python main.py` çalıştır.")
else:
    st.info("Henüz `daily_signals.json` yok. Terminalde `python main.py` çalıştır.")

st.divider()

# ------------------------------------------------------------
# Fırsat listesi
# ------------------------------------------------------------
st.subheader("🔥 En Güçlü Sinyaller")

if posts:
    rows = []
    for p in posts:
        points = p.get("points") or p.get("score") or 0
        if points < min_points:
            continue
        rows.append({
            "Başlık": (p.get("title") or "")[:80],
            "Kaynak": p.get("source", ""),
            "Puan": points,
            "Yorum": p.get("comments", 0),
            "URL": p.get("url", ""),
        })

    if rows:
        df = pd.DataFrame(rows).sort_values("Puan", ascending=False).head(top_n)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "URL": st.column_config.LinkColumn("Link"),
                "Puan": st.column_config.ProgressColumn(
                    "Puan", min_value=0, max_value=max(df["Puan"].max(), 1), format="%d"
                ),
            },
        )

        st.subheader("📊 Puan Dağılımı (Top)")
        chart_df = df.set_index("Başlık")[["Puan"]]
        st.bar_chart(chart_df)
    else:
        st.warning("Filtrelere uyan sinyal yok.")
else:
    st.warning("Sinyal verisi yok.")

st.divider()

# ------------------------------------------------------------
# Opportunity Monitor
# ------------------------------------------------------------
st.subheader("👁️ Opportunity Monitor")

if isinstance(tracked_data, list) and tracked_data:
    mon_rows = []
    for t in tracked_data:
        mon_rows.append({
            "ID": t.get("id", ""),
            "Başlık": (t.get("title") or "")[:60],
            "Skor": f"{t.get('original_score', 0)} → {t.get('current_score', 0)}",
            "Durum": t.get("status", ""),
            "Uyarı": len(t.get("alerts", [])),
            "Son kontrol": (t.get("last_checked") or "")[:10],
        })
    mon_df = pd.DataFrame(mon_rows)
    st.dataframe(mon_df, hide_index=True, use_container_width=True)

    status_counts = {}
    for t in tracked_data:
        s = t.get("status", "stable")
        status_counts[s] = status_counts.get(s, 0) + 1
    if status_counts:
        st.bar_chart(pd.DataFrame({"Adet": status_counts}))
else:
    st.info("Henüz takip edilen fırsat yok. `python main.py` yüksek skorluları otomatik ekler.")

st.divider()
st.caption(f"AI Opportunity Hunter • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
