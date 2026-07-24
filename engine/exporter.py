"""
AI Opportunity Hunter
Exporter Engine

Görevi:
- JSON dosyalarını kaydetmek
- JSON dosyalarını okumak
"""

import json


from config import (
    DAILY_SIGNALS_FILE,
    OPPORTUNITIES_FILE,
    TRACKED_FILE,
)


def save_daily_signals(data: dict):

    DAILY_SIGNALS_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

    with open(
        DAILY_SIGNALS_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_daily_signals():

    if not DAILY_SIGNALS_FILE.exists():
        return {
            "posts": [],
            "sources": {},
            "fetched_at": "",
        }

    with open(
        DAILY_SIGNALS_FILE,
        encoding="utf-8",
    ) as f:

        return json.load(f)


def load_tracked():

    if not TRACKED_FILE.exists():
        return {
            "opportunities": []
        }

    with open(
        TRACKED_FILE,
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_tracked(data):

    TRACKED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        TRACKED_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

def save_opportunities(data):

    OPPORTUNITIES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OPPORTUNITIES_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_opportunities():

    if not OPPORTUNITIES_FILE.exists():
        return []

    with open(
        OPPORTUNITIES_FILE,
        encoding="utf-8",
    ) as f:

        return json.load(f)
