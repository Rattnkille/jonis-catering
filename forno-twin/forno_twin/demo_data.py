"""Lädt die synthetischen Demo-Events (klar als synthetisch gekennzeichnet)."""
from __future__ import annotations

import json
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "synthetic_events.json"


def load_events() -> list[dict]:
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)["events"]
