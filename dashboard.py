#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opportunity Intelligence Platform (OIP) – Official Production Dashboard V1.

Professional single-file Streamlit dashboard for the Opportunity Intelligence
Platform. Visualises opportunity signals collected from multiple providers and
helps founders discover high-quality business opportunities.

Data sources (existing project artefacts only):
    daily_signals.json
    tracked_opportunities.json

The application never invents data, never crashes on missing or malformed
files, and degrades gracefully with clear Streamlit warnings.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION: str = "1.0.0"
APP_TITLE: str = "Opportunity Intelligence Platform"
APP_SHORT: str = "OIP"
PAGE_ICON: str = "🎯"

DAILY_SIGNALS_PATH: Path = Path("daily_signals.json")
TRACKED_OPPORTUNITIES_PATH: Path = Path("tracked_opportunities.json")

LOG_DIR: Path = Path("logs")
LOG_FILE: str = "dashboard.log"

HIGH_CONFIDENCE_THRESHOLD: float = 75.0
CACHE_TTL_SECONDS: int = 60

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging() -> logging.Logger:
    """Configure structured application logging to file and stdout.

    Returns:
        Configured logger instance.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("oip.dashboard")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(LOG_DIR / LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


logger = setup_logging()

# ---------------------------------------------------------------------------
# Data loading & normalisation
# ---------------------------------------------------------------------------


def load_json_safely(path: Path) -> Tuple[Optional[Any], Optional[str]]:
    """Load a JSON file without raising exceptions.

    Args:
        path: Filesystem path to the JSON document.

    Returns:
        Tuple of (parsed object or None, human-readable error message or None).
    """
    if not path.is_file():
        return None, f"Dosya bulunamadı: `{path.name}`"
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data, None
    except json.JSONDecodeError as exc:
        logger.error("JSON decode failure in %s: %s", path, exc)
        return None, f"Geçersiz JSON formatı: `{path.name}`"
    except OSError as exc:
        logger.error("I/O failure reading %s: %s", path, exc)
        return None, f"Okuma hatası: `{path.name}`"


def extract_records(raw: Any, source_name: str) -> List[Dict[str, Any]]:
    """Normalise heterogeneous JSON shapes into a flat list of dictionaries.

    Accepted shapes:
        * list[dict]
        * dict containing one of the keys: opportunities, signals, items,
          data, results
        * a single dict (wrapped into a one-element list)

    Args:
        raw: Parsed JSON content.
        source_name: Identifier used only for logging.

    Returns:
        List of opportunity dictionaries (may be empty).
    """
    if raw is None:
        return []

    records: List[Dict[str, Any]] = []
    if isinstance(raw, list):
        records = [item for item in raw if isinstance(item, dict)]
    elif isinstance(raw, dict):
        for key in ("opportunities", "signals", "items", "data", "results"):
            candidate = raw.get(key)
            if isinstance(candidate, list):
                records = [item for item in candidate if isinstance(item, dict)]
                break
        else:
            records = [raw]
    else:
        logger.warning("Unexpected root type from %s: %s", source_name, type(raw))
        return []

    logger.info("Extracted %d record(s) from %s", len(records), source_name)
    return records


def records_to_dataframe(records: Sequence[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a sequence of opportunity dictionaries into a normalised DataFrame.

    Missing columns are filled with sensible defaults. Score and confidence
    are coerced to numeric. Timestamps are parsed best-effort.

    Args:
        records: Sequence of opportunity dictionaries.

    Returns:
        Clean pandas DataFrame ready for filtering and visualisation.
    """
    columns = [
        "id",
        "title",
        "description",
        "score",
        "confidence",
        "provider",
        "category",
        "reason",
        "url",
        "status",
        "timestamp",
    ]

    if not records:
        return pd.DataFrame(columns=columns)

    frame = pd.DataFrame(records)

    defaults: Dict[str, Any] = {
        "id": "",
        "title": "Untitled",
        "description": "",
        "score": 0.0,
        "confidence": 0.0,
        "provider": "unknown",
        "category": "",
        "reason": "",
        "url": "",
        "status": "",
        "timestamp": "",
    }
    for col, default in defaults.items():
        if col not in frame.columns:
            frame[col] = default

    frame["score"] = pd.to_numeric(frame["score"], errors="coerce").fillna(0.0)
    # Prefer explicit confidence; fall back to score when absent or zero
    frame["confidence"] = pd.to_numeric(frame["confidence"], errors="coerce")
    frame["confidence"] = frame["confidence"].fillna(frame["score"])

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"], errors="coerce", utc=True
    )

    for col in ("id", "title", "description", "provider", "category", "reason", "url", "status"):
        frame[col] = frame[col].astype(str).replace({"nan": "", "None": "", "NaT": ""})

    return frame[columns]


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_all_data() -> Tuple[pd.DataFrame, List[str]]:
    """Load and merge daily signals together with tracked opportunities.

    Returns:
        Tuple of (combined DataFrame, list of warning messages).
    """
    warnings: List[str] = []
    frames: List[pd.DataFrame] = []

    for path in (DAILY_SIGNALS_PATH, TRACKED_OPPORTUNITIES_PATH):
        raw, error = load_json_safely(path)
        if error:
            warnings.append(error)
            continue
        records = extract_records(raw, path.name)
        if records:
            frames.append(records_to_dataframe(records))

    if not frames:
        empty = records_to_dataframe([])
        return empty, warnings

    combined = pd.concat(frames, ignore_index=True)

    # Prefer higher-score record when duplicate ids exist
    if combined["id"].ne("").any():
        combined = (
            combined.sort_values("score", ascending=False)
            .drop_duplicates(subset=["id"], keep="first")
            .reset_index(drop=True)
        )
    else:
        combined = combined.drop_duplicates(
            subset=["title", "provider"], keep="first"
        ).reset_index(drop=True)

    return combined, warnings


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def apply_filters(
    df: pd.DataFrame,
    min_score: float,
    selected_providers: Sequence[str],
    search_term: str,
) -> pd.DataFrame:
    """Apply sidebar filters to the opportunity DataFrame.

    Args:
        df: Source DataFrame.
        min_score: Minimum score threshold (inclusive).
        selected_providers: Provider names to keep; empty means all.
        search_term: Case-insensitive free-text query.

    Returns:
        Filtered DataFrame (new object).
    """
    if df.empty:
        return df.copy()

    filtered = df[df["score"] >= min_score].copy()

    if selected_providers:
        filtered = filtered[filtered["provider"].isin(selected_providers)]

    term = search_term.strip().lower()
    if term:
        mask = (
            filtered["title"].str.lower().str.contains(term, na=False)
            | filtered["description"].str.lower().str.contains(term, na=False)
            | filtered["provider"].str.lower().str.contains(term, na=False)
            | filtered["category"].str.lower().str.contains(term, na=False)
            | filtered["reason"].str.lower().str.contains(term, na=False)
        )
        filtered = filtered[mask]

    return filtered.reset_index(drop=True)


# ---------------------------------------------------------------------------
# UI – styling
# ---------------------------------------------------------------------------


def inject_dark_theme() -> None:
    """Inject professional dark-theme CSS overrides."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: #e6edf3;
        }
        section[data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        div[data-testid="stMetric"] {
            background-color: #1c2128;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 14px 18px;
        }
        div[data-testid="stMetric"] label {
            color: #8b949e !important;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #f0f6fc !important;
            font-weight: 600;
        }
        h1, h2, h3, h4 {
            color: #f0f6fc !important;
        }
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #388bfd;
            background-color: #21262d;
            color: #e6edf3;
        }
        .stButton > button:hover {
            border-color: #58a6ff;
            background-color: #30363d;
        }
        div[data-testid="stAlert"] {
            border-radius: 8px;
        }
        .opportunity-card {
            background-color: #1c2128;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .opportunity-card h4 {
            margin: 0 0 8px 0;
            color: #58a6ff !important;
        }
        .meta-label {
            color: #8b949e;
            font-size: 0.85rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# UI – components
# ---------------------------------------------------------------------------


def render_hero(last_refresh: str, record_count: int) -> None:
    """Render the hero header with title, status and version.

    Args:
        last_refresh: Human-readable last-refresh timestamp.
        record_count: Total number of records currently loaded.
    """
    status = "Operational" if record_count > 0 else "No data"
    status_colour = "#3fb950" if record_count > 0 else "#d29922"

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:1.5rem;flex-wrap:wrap;gap:12px;">
            <div>
                <h1 style="margin:0;font-size:1.9rem;">{PAGE_ICON} {APP_TITLE}</h1>
                <p style="margin:4px 0 0 0;color:#8b949e;">
                    AI-powered startup opportunity intelligence
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.9rem;color:#8b949e;">
                    Last refresh · {last_refresh}
                </div>
                <div style="font-size:0.9rem;">
                    <span style="color:{status_colour};">●</span>
                    {status}&nbsp;&nbsp;|&nbsp;&nbsp;v{VERSION}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(df: pd.DataFrame) -> None:
    """Render the four primary KPI metric cards.

    Args:
        df: Currently filtered opportunities DataFrame.
    """
    total = len(df)
    avg_score = float(df["score"].mean()) if total else 0.0
    providers = int(df["provider"].nunique()) if total else 0
    high_conf = int((df["confidence"] >= HIGH_CONFIDENCE_THRESHOLD).sum()) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Opportunities", f"{total:,}")
    c2.metric("Average Score", f"{avg_score:.1f}")
    c3.metric("Providers", f"{providers}")
    c4.metric("High Confidence", f"{high_conf}")


def render_score_chart(df: pd.DataFrame) -> None:
    """Render score distribution histogram."""
    if df.empty:
        st.info("Skor dağılımı için veri yok.")
        return
    fig = px.histogram(
        df,
        x="score",
        nbins=20,
        title="Score Distribution",
        labels={"score": "Score", "count": "Count"},
        color_discrete_sequence=["#388bfd"],
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_provider_chart(df: pd.DataFrame) -> None:
    """Render provider distribution bar chart."""
    if df.empty:
        st.info("Provider dağılımı için veri yok.")
        return
    counts = (
        df["provider"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["Provider", "Count"]
    fig = px.bar(
        counts,
        x="Provider",
        y="Count",
        title="Provider Distribution",
        color="Count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_chart(df: pd.DataFrame) -> None:
    """Render confidence distribution histogram."""
    if df.empty:
        st.info("Confidence dağılımı için veri yok.")
        return
    fig = px.histogram(
        df,
        x="confidence",
        nbins=20,
        title="Confidence Distribution",
        labels={"confidence": "Confidence", "count": "Count"},
        color_discrete_sequence=["#3fb950"],
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_timeline_chart(df: pd.DataFrame) -> None:
    """Render opportunity timeline if timestamp data exists."""
    if df.empty or df["timestamp"].isna().all():
        st.info("Zaman çizelgesi için geçerli timestamp verisi yok.")
        return
    timeline = (
        df.dropna(subset=["timestamp"])
        .assign(date=lambda x: x["timestamp"].dt.date)
        .groupby("date")
        .size()
        .reset_index(name="count")
        .sort_values("date")
    )
    fig = px.area(
        timeline,
        x="date",
        y="count",
        title="Opportunity Timeline",
        labels={"date": "Date", "count": "Opportunities"},
        color_discrete_sequence=["#a371f7"],
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_top_opportunity_cards(df: pd.DataFrame, limit: int = 6) -> None:
    """Render top opportunities as visual cards.

    Args:
        df: Filtered DataFrame.
        limit: Maximum number of cards to display.
    """
    if df.empty:
        st.info("Top opportunities için veri yok.")
        return

    top = df.nlargest(limit, "score")
    cols = st.columns(min(3, len(top)))

    for idx, (_, row) in enumerate(top.iterrows()):
        col = cols[idx % len(cols)]
        with col:
            title = row["title"][:80] + ("…" if len(row["title"]) > 80 else "")
            reason = row["reason"][:120] + ("…" if len(str(row["reason"])) > 120 else "")
            st.markdown(
                f"""
                <div class="opportunity-card">
                    <h4>{title}</h4>
                    <div class="meta-label">Score</div>
                    <div style="font-size:1.4rem;font-weight:600;color:#58a6ff;">
                        {row['score']:.1f}
                    </div>
                    <div class="meta-label" style="margin-top:8px;">Confidence</div>
                    <div>{row['confidence']:.1f}</div>
                    <div class="meta-label" style="margin-top:8px;">Category</div>
                    <div>{row['category'] or '—'}</div>
                    <div class="meta-label" style="margin-top:8px;">Reason</div>
                    <div style="font-size:0.9rem;">{reason or '—'}</div>
                    <div class="meta-label" style="margin-top:8px;">Provider</div>
                    <div>{row['provider']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_recent_table(df: pd.DataFrame, limit: int = 10) -> None:
    """Render the most recent opportunities table."""
    if df.empty:
        st.info("Recent opportunities için veri yok.")
        return

    recent = (
        df.sort_values("timestamp", ascending=False)
        .head(limit)[
            ["title", "score", "confidence", "provider", "category", "timestamp", "url"]
        ]
        .copy()
    )
    recent["timestamp"] = recent["timestamp"].apply(
        lambda ts: ts.strftime("%Y-%m-%d %H:%M") if pd.notna(ts) else "—"
    )
    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Title", width="large"),
            "score": st.column_config.NumberColumn("Score", format="%.1f"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.1f"),
            "provider": "Provider",
            "category": "Category",
            "timestamp": "Timestamp",
            "url": st.column_config.LinkColumn("URL"),
        },
    )


def render_full_table(df: pd.DataFrame) -> None:
    """Render the complete sortable opportunity table."""
    if df.empty:
        st.info("Görüntülenecek fırsat bulunamadı.")
        return

    display = df[
        [
            "title",
            "score",
            "confidence",
            "provider",
            "category",
            "status",
            "reason",
            "timestamp",
            "url",
            "description",
        ]
    ].copy()
    display["timestamp"] = display["timestamp"].apply(
        lambda ts: ts.strftime("%Y-%m-%d %H:%M") if pd.notna(ts) else "—"
    )
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=440,
        column_config={
            "title": st.column_config.TextColumn("Title", width="medium"),
            "score": st.column_config.NumberColumn("Score", format="%.1f"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.1f"),
            "provider": "Provider",
            "category": "Category",
            "status": "Status",
            "reason": st.column_config.TextColumn("Reason", width="medium"),
            "timestamp": "Timestamp",
            "url": st.column_config.LinkColumn("URL"),
            "description": st.column_config.TextColumn("Description", width="large"),
        },
    )


def render_export_buttons(df: pd.DataFrame) -> None:
    """Render CSV and JSON download buttons."""
    if df.empty:
        return

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    col1, col2, _ = st.columns([1, 1, 3])

    csv_data = df.to_csv(index=False).encode("utf-8")
    col1.download_button(
        label="📥 Export CSV",
        data=csv_data,
        file_name=f"oip_opportunities_{ts}.csv",
        mime="text/csv",
    )

    # Convert timestamps to ISO strings for JSON serialisation
    export_df = df.copy()
    if "timestamp" in export_df.columns:
        export_df["timestamp"] = export_df["timestamp"].apply(
            lambda ts: ts.isoformat() if pd.notna(ts) else None
        )
    json_data = export_df.to_json(orient="records", force_ascii=False, indent=2)
    col2.download_button(
        label="📥 Export JSON",
        data=json_data,
        file_name=f"oip_opportunities_{ts}.json",
        mime="application/json",
    )


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for the Opportunity Intelligence Platform dashboard."""
    st.set_page_config(
        page_title=f"{APP_SHORT} – {APP_TITLE}",
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_dark_theme()

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------
    with st.sidebar:
        st.markdown(f"### {PAGE_ICON} {APP_SHORT} Controls")

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        min_score = st.slider(
            "Minimum Score",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
            help="Only opportunities with score ≥ this value are shown",
        )

        # Load data so provider list is available
        df_raw, load_warnings = load_all_data()
        all_providers = (
            sorted(df_raw["provider"].dropna().unique().tolist())
            if not df_raw.empty
            else []
        )
        selected_providers = st.multiselect(
            "Provider Filter",
            options=all_providers,
            default=[],
            help="Leave empty to include every provider",
        )

        search_query = st.text_input(
            "Search",
            value="",
            placeholder="Title, description, category, reason…",
            help="Case-insensitive free-text search across key fields",
        )

        st.divider()
        st.markdown("**Theme**")
        st.caption("Professional Dark · System")
        st.markdown("**Statistics**")
        st.caption(f"Raw records loaded: {len(df_raw)}")
        st.caption(f"High-confidence threshold: {HIGH_CONFIDENCE_THRESHOLD}")
        st.caption(f"Cache TTL: {CACHE_TTL_SECONDS}s")
        st.caption(f"Version: {VERSION}")

    # ------------------------------------------------------------------
    # Warnings
    # ------------------------------------------------------------------
    for message in load_warnings:
        st.warning(message)

    # ------------------------------------------------------------------
    # Filter
    # ------------------------------------------------------------------
    df = apply_filters(df_raw, min_score, selected_providers, search_query)

    last_refresh = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # ------------------------------------------------------------------
    # Hero
    # ------------------------------------------------------------------
    render_hero(last_refresh, len(df_raw))

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------
    st.subheader("Overview")
    render_kpi_cards(df)

    st.divider()

    # ------------------------------------------------------------------
    # Charts – row 1
    # ------------------------------------------------------------------
    chart1, chart2 = st.columns(2)
    with chart1:
        st.subheader("Score Distribution")
        render_score_chart(df)
    with chart2:
        st.subheader("Provider Distribution")
        render_provider_chart(df)

    # ------------------------------------------------------------------
    # Charts – row 2
    # ------------------------------------------------------------------
    chart3, chart4 = st.columns(2)
    with chart3:
        st.subheader("Confidence Distribution")
        render_confidence_chart(df)
    with chart4:
        st.subheader("Timeline")
        render_timeline_chart(df)

    st.divider()

    # ------------------------------------------------------------------
    # Top Opportunities (cards)
    # ------------------------------------------------------------------
    st.subheader("Top Opportunities")
    render_top_opportunity_cards(df, limit=6)

    st.divider()

    # ------------------------------------------------------------------
    # Recent
    # ------------------------------------------------------------------
    st.subheader("Recent Opportunities")
    render_recent_table(df, limit=10)

    st.divider()

    # ------------------------------------------------------------------
    # Full table + export
    # ------------------------------------------------------------------
    st.subheader("All Opportunities")
    render_full_table(df)
    render_export_buttons(df)

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    st.divider()
    st.caption(
        f"{APP_TITLE} · Dashboard v{VERSION} · "
        f"{len(df_raw)} total records · "
        f"Filtered view: {len(df)} opportunities"
    )


if __name__ == "__main__":
    main()
