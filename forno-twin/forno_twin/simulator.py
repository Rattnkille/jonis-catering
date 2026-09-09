"""Was-wäre-wenn-Simulator: drei Störungen mit Vorher-Nachher-Vergleich."""
from __future__ import annotations

import copy

from .planning import plan
from .calc import calculate
from .schema import EventFile

SCENARIOS = {
    "plus20": {"name": "+20 % Gäste", "desc": "Kurzfristig 20 Prozent mehr Gäste als angekündigt"},
    "more_veg": {"name": "Mehr vegetarisch/vegan", "desc": "Vegetarischer Anteil 60 %, veganer Anteil 25 % statt geplant"},
    "rain_delay": {"name": "Regen + 30 min Verzögerung + 1 Helfer fällt aus",
                   "desc": "Wetterschutz nötig, Servierbeginn 30 min später, ein Helfer krank"},
}


def _snapshot(ev: EventFile, package: str, params=None, helper_delta: int = 0, delay_min: int = 0) -> dict:
    pl = plan(ev, package, params)
    helpers = max(1, pl["staff"]["helpers"] + helper_delta)
    hours = pl["staff"]["hours_per_helper"] + delay_min / 60
    calc = calculate(ev.guests or 0, package, helpers=helpers, hours=hours, params=params)
    return {"plan": pl, "calc": calc, "helpers": helpers, "hours": hours}


def simulate(ev: EventFile, package: str, scenario: str, params=None) -> dict:
    before = _snapshot(ev, package, params)
    ev2 = copy.deepcopy(ev)
    measures = []
    helper_delta, delay = 0, 0
    if scenario == "plus20":
        ev2.guests = int(round((ev.guests or 0) * 1.2))
        measures = ["Nachbestellung Mehl/Käse/Beläge laut Differenz", "Teig: zusätzliche Teiglinge T-36h ansetzen",
                    "Ofenkapazität neu prüfen; ggf. Servierzeit +30 min mit Kunde vereinbaren", "Nachberechnung Angebot (Preis p.P. × Mehrgäste)"]
    elif scenario == "more_veg":
        ev2.veg_share, ev2.vegan_share = 0.60, 0.25
        measures = ["Sortenverteilung live anpassen (Pizza Pulse)", "Zweite vegane Sorte (La Verde) einplanen",
                    "Fior di Latte reduzieren, Gemüsebeläge erhöhen", "Fleischbeläge vakuumiert zurücknehmen (weniger Verlust)"]
    elif scenario == "rain_delay":
        ev2.weather_protection = True
        helper_delta, delay = -1, 30
        measures = ["Pavillon/Wetterschutz über Ausgabe aufbauen (T-3h Wetter-Check)", "Servierzeit um 30 min nach hinten schieben, Kunde informieren",
                    "Rollen neu verteilen: Pizzaiolo backt, 1 Person Teig + Ausgabe", "Ersatzhelfer aus Bereitschaftsliste anrufen (TBD: Liste existiert?)",
                    "Kürzere Sortenkarte (4 statt 6) zur Entlastung"]
    else:
        raise ValueError(f"Unbekanntes Szenario {scenario}")
    after = _snapshot(ev2, package, params, helper_delta, delay)

    def diff(key_path):
        a, b = before, after
        for k in key_path:
            a, b = a[k], b[k]
        return {"before": a, "after": b, "delta": (round(b - a, 2) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None)}

    changes = {
        "guests": diff(["plan", "guests"]),
        "pizzas_total": diff(["plan", "pizzas_total"]),
        "dough_kg": diff(["plan", "dough_kg"]),
        "helpers": diff(["helpers"]),
        "hours_per_helper": diff(["hours"]),
        "oven_needed_per_hour": diff(["plan", "oven", "needed_per_hour"]),
        "oven_ok": diff(["plan", "oven", "ok"]),
        "umsatz_netto": diff(["calc", "results", "umsatz_netto"]),
        "ware": diff(["calc", "results", "ware"]),
        "personal": diff(["calc", "results", "personal"]),
        "gewinn": diff(["calc", "results", "gewinn"]),
        "prime_cost_pct": diff(["calc", "results", "prime_cost_pct"]),
    }
    shopping_diff = []
    b_items = {s["item"]: s for s in before["plan"]["shopping"]}
    for s in after["plan"]["shopping"]:
        b = b_items.get(s["item"], {"qty": 0})
        if s["qty"] != b["qty"]:
            shopping_diff.append({"item": s["item"], "before": b["qty"], "after": s["qty"], "unit": s["unit"]})
    risk_delta = []
    if not after["plan"]["oven"]["ok"]:
        risk_delta.append("Ofenkapazität überschritten (Parameterstatus TBD – reale Kapazität messen!)")
    if after["helpers"] < before["helpers"]:
        risk_delta.append("Personalunterdeckung: Servicequalität und Pausen gefährdet")
    if scenario == "rain_delay":
        risk_delta.append("Nässe: Holz trocken lagern, Stromkabel schützen, Rutschgefahr am Ausgabeplatz")
    return {"scenario": scenario, "name": SCENARIOS[scenario]["name"], "desc": SCENARIOS[scenario]["desc"],
            "changes": changes, "shopping_diff": shopping_diff, "distribution_after": after["plan"]["distribution"],
            "measures": measures, "risk_delta": risk_delta,
            "note": "Kostenwerte basieren auf ANNAHME-Parametern; Richtung und Größenordnung sind belastbar, Beträge nicht."}


def simulate_all(ev: EventFile, package: str, params=None) -> list[dict]:
    return [simulate(ev, package, s, params) for s in SCENARIOS]
