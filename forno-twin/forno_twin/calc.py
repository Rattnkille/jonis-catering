"""Kalkulation – spiegelt exakt die Formeln aus kalkulation.html (Prime-Cost-Rechner).

Alle Standardwerte tragen Status ANNAHME (Rechner-Defaults, keine Ist-Kosten).
Ergebnis enthält Fakten, Formeln, Annahmen und Unsicherheitsband.
"""
from __future__ import annotations

from .knowledge import PACKAGES, CALC_DEFAULTS, CALC_DEFAULTS_STATUS, CALC_DEFAULTS_SOURCE, ANNAHME, VERIFIZIERT, TBD
from .params import load_params, p


def calculate(guests: int, package: str = "classic", helpers: float | None = None, hours: float | None = None,
              overrides: dict | None = None, params: dict | None = None) -> dict:
    params = params or load_params()
    o = {**CALC_DEFAULTS, **(overrides or {})}
    pkg = PACKAGES[package]
    price = pkg["price_pp_brutto"]
    vat = 0.19
    helpers = helpers if helpers is not None else o["helfer"]
    hours = hours if hours is not None else o["stunden_pro_helfer"]

    umsatz_brutto = guests * price
    umsatz_netto = umsatz_brutto / (1 + vat)
    ware = guests * o["ware_pro_gast_netto"] + o["ware_pauschal"]
    lohn_brutto = helpers * hours * o["stundenlohn"]
    personal = lohn_brutto * (1 + o["ag_pauschale_pct"] / 100)
    fix = o["fixkosten_anteil"]
    prime = ware + personal
    prime_pct = (prime / umsatz_netto * 100) if umsatz_netto else 0
    gewinn = umsatz_netto - prime - fix
    gewinn_pct = (gewinn / umsatz_netto * 100) if umsatz_netto else 0

    uw = p(params, "ware_uncertainty"); up = p(params, "personal_uncertainty")
    gewinn_low = umsatz_netto - ware * (1 + uw) - personal * (1 + up) - fix
    gewinn_high = umsatz_netto - ware * (1 - uw) - personal * (1 - up) - fix

    if prime_pct < 55: status = "sehr gut"
    elif prime_pct < 60: status = "gesund"
    elif prime_pct < 65: status = "grenzwertig"
    else: status = "kritisch"

    lohn_pro_event = hours * o["stundenlohn"]
    minijob = None
    if lohn_pro_event > 0:
        minijob = {"max_events_per_month": int(o["minijob_grenze"] // lohn_pro_event) if lohn_pro_event <= o["minijob_grenze"] else 0,
                   "note": f"{o['minijob_grenze']:.0f} €-Grenze (kalkulation.html)"}

    return {
        "inputs": {
            "guests": {"value": guests, "status": VERIFIZIERT, "source": "Eventakte"},
            "price_pp_brutto": {"value": price, "status": pkg["price_status"], "source": pkg["source"]},
            "vat_pct": {"value": 19, "status": "ABLEITUNG", "source": "kalkulation.html Standard"},
            "ware_pro_gast_netto": {"value": o["ware_pro_gast_netto"], "status": CALC_DEFAULTS_STATUS, "source": CALC_DEFAULTS_SOURCE},
            "ware_pauschal": {"value": o["ware_pauschal"], "status": CALC_DEFAULTS_STATUS, "source": CALC_DEFAULTS_SOURCE},
            "helpers": {"value": helpers, "status": "ABLEITUNG" if helpers != o["helfer"] else CALC_DEFAULTS_STATUS, "source": "Planung / Rechner-Default"},
            "hours_per_helper": {"value": hours, "status": "ABLEITUNG" if hours != o["stunden_pro_helfer"] else CALC_DEFAULTS_STATUS, "source": "Planung / Rechner-Default"},
            "stundenlohn": {"value": o["stundenlohn"], "status": CALC_DEFAULTS_STATUS, "source": CALC_DEFAULTS_SOURCE},
            "ag_pauschale_pct": {"value": o["ag_pauschale_pct"], "status": CALC_DEFAULTS_STATUS, "source": CALC_DEFAULTS_SOURCE},
            "fixkosten_anteil": {"value": fix, "status": CALC_DEFAULTS_STATUS, "source": CALC_DEFAULTS_SOURCE},
            "fahrtkostenpauschale": {"value": None, "status": TBD, "source": "Website nennt Pauschale >10 km ohne Betrag"},
        },
        "formulas": {
            "umsatz_netto": "Gäste × Preis brutto / (1 + USt)",
            "ware": "Gäste × Ware/Gast + Pauschale",
            "personal": "Helfer × Stunden × Lohn × (1 + AG-Pauschale)",
            "prime_cost": "Ware + Personal",
            "gewinn": "Umsatz netto − Prime Cost − Fixkosten-Anteil",
        },
        "results": {
            "umsatz_brutto": round(umsatz_brutto, 2), "umsatz_netto": round(umsatz_netto, 2),
            "ware": round(ware, 2), "personal": round(personal, 2), "fix": round(fix, 2),
            "prime_cost": round(prime, 2), "prime_cost_pct": round(prime_pct, 1), "prime_status": status,
            "gewinn": round(gewinn, 2), "gewinn_pct": round(gewinn_pct, 1),
            "gewinn_band": [round(gewinn_low, 2), round(gewinn_high, 2)],
            "band_note": f"Ware ±{uw:.0%}, Personal ±{up:.0%} (ANNAHME); Fahrtkosten >10 km nicht enthalten (TBD)",
        },
        "minijob": minijob,
        "approval_required": True,
        "warning": "Alle Kostenwerte sind Rechner-Standardwerte (ANNAHME), keine verifizierten Ist-Kosten.",
    }
