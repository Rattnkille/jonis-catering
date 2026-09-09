"""Lernen nach dem Event ('Waste Lens') und Kalibrierung der Planungsparameter.

Eingabe: Ist-Daten pro Event (manuell erfasst, gewogen). Fotos dürfen Kategorien
stützen, aber nie Gewicht, Allergene oder Lebensmittelsicherheit vortäuschen.
Ausgabe: Abweichungen, Verbesserungshinweise, gedämpfte Parameter-Updates.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .params import CALIB_PATH, load_params

ACTUALS_DIR = Path(__file__).resolve().parent.parent / "data" / "actuals"


def waste_lens(planned: dict, actual: dict) -> dict:
    """Vergleicht Plan (plan()-Output) mit Ist (produziert, übrig, Personal, Zeiten)."""
    produced = actual.get("pizzas_produced")
    leftover_dough = actual.get("leftover_dough_kg", 0.0)
    leftover_pizzas = actual.get("leftover_pizzas", 0)
    guests_actual = actual.get("guests_actual", planned["guests"])
    eaten = (produced or 0) - leftover_pizzas
    pp_actual = eaten / guests_actual if guests_actual else None
    rows = [
        {"metric": "Gäste", "plan": planned["guests"], "ist": guests_actual},
        {"metric": "Pizzen produziert", "plan": planned["pizzas_total"], "ist": produced},
        {"metric": "Pizzen übrig", "plan": 0, "ist": leftover_pizzas},
        {"metric": "Teig übrig (kg)", "plan": 0, "ist": leftover_dough},
        {"metric": "Pizzen pro Gast (gegessen)", "plan": planned["pizzas_pp"], "ist": round(pp_actual, 2) if pp_actual else None},
        {"metric": "Helfer", "plan": planned["staff"]["helpers"], "ist": actual.get("helpers_actual")},
        {"metric": "Stunden je Helfer", "plan": planned["staff"]["hours_per_helper"], "ist": actual.get("hours_per_helper_actual")},
        {"metric": "Servierdauer (min)", "plan": None, "ist": actual.get("serving_minutes_actual")},
    ]
    hints = []
    if produced and planned["pizzas_total"]:
        dev = (produced - planned["pizzas_total"]) / planned["pizzas_total"]
        if abs(dev) > 0.1:
            hints.append(f"Produktionsmenge weicht {dev:+.0%} vom Plan ab. Puffer oder Pizzen p.P. anpassen.")
    if leftover_dough and planned["dough_kg"] and leftover_dough / planned["dough_kg"] > 0.1:
        hints.append(f"{leftover_dough / planned['dough_kg']:.0%} Teig übrig. Teigling oder Puffer reduzieren.")
    if pp_actual and abs(pp_actual - planned["pizzas_pp"]) > 0.2:
        hints.append(f"Gäste haben {pp_actual:.2f} Pizzen gegessen (Plan {planned['pizzas_pp']}). Parameter kalibrieren.")
    sort_hint = []
    for s in actual.get("leftover_by_sort", []):
        sort_hint.append(f"{s['name']}: {s['leftover']} übrig")
    if sort_hint:
        hints.append("Restmengen nach Sorte: " + ", ".join(sort_hint))
    if actual.get("serving_minutes_actual") and actual.get("pizzas_produced"):
        rate = actual["pizzas_produced"] / (actual["serving_minutes_actual"] / 60)
        hints.append(f"Gemessene Ofenleistung: {rate:.0f} Pizzen/h. Dieser Wert kalibriert 'oven_pizzas_per_hour'.")
    return {"rows": rows, "hints": hints, "photo_policy": "Fotos nur zur Kategorisierung; Gewichte manuell gewogen."}


def load_actuals(directory: Path | None = None) -> list[dict]:
    directory = directory or ACTUALS_DIR
    out = []
    if directory.exists():
        for f in sorted(directory.glob("*.json")):
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
                d["_file"] = f.name
                out.append(d)
    return out


def calibrate(actuals: list[dict] | None = None, alpha: float = 0.3, write: bool = True, min_events: int = 2) -> dict:
    """Gedämpfte Kalibrierung (EMA) aus Ist-Daten. Nur reale (nicht-synthetische) Events zählen.

    - pizzas_per_guest_observed -> dokumentiert, Paketwert bleibt (Geschäftsentscheidung)
    - oven_pizzas_per_hour       <- gemessene Ofenleistung
    - guests_per_helper          <- Gäste / eingesetzte Helfer
    - safety_buffer              <- Restquote (Ziel: 5-10 %)
    """
    actuals = actuals if actuals is not None else load_actuals()
    real = [a for a in actuals if not a.get("synthetic", True)]
    base = load_params(with_calibration=False)
    overrides, notes = {}, []
    if len(real) < min_events:
        notes.append(f"Nur {len(real)} reale Events mit Ist-Daten (Minimum {min_events}). Keine Kalibrierung, Parameter bleiben ANNAHME.")
        result = {"updated": date.today().isoformat(), "n_real_events": len(real), "overrides": {}, "notes": notes}
    else:
        def ema(key, observed):
            cur = base[key]["value"]
            for v in observed:
                cur = (1 - alpha) * cur + alpha * v
            return round(cur, 3)
        rates = [a["pizzas_produced"] / (a["serving_minutes_actual"] / 60) for a in real if a.get("serving_minutes_actual") and a.get("pizzas_produced")]
        if rates:
            overrides["oven_pizzas_per_hour"] = {"value": ema("oven_pizzas_per_hour", rates), "n_events": len(rates), "updated": date.today().isoformat()}
        gph = [a["guests_actual"] / a["helpers_actual"] for a in real if a.get("helpers_actual") and a.get("guests_actual")]
        if gph:
            overrides["guests_per_helper"] = {"value": ema("guests_per_helper", gph), "n_events": len(gph), "updated": date.today().isoformat()}
        left = [a["leftover_pizzas"] / a["pizzas_produced"] for a in real if a.get("pizzas_produced") and a.get("leftover_pizzas") is not None]
        if left:
            target = 0.07
            adj = [max(0.03, min(0.2, base["safety_buffer"]["value"] - (l - target))) for l in left]
            overrides["safety_buffer"] = {"value": ema("safety_buffer", adj), "n_events": len(adj), "updated": date.today().isoformat()}
        result = {"updated": date.today().isoformat(), "n_real_events": len(real), "overrides": overrides,
                  "notes": notes + [f"EMA alpha={alpha}; Basis = parameters.json"]}
    if write:
        CALIB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CALIB_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result
