"""Deterministische Mengen-, Einkaufs-, Personal- und Zeitplanung.

Jede Zahl entsteht aus sichtbaren Formeln mit Parametern, deren Status
(VERIFIZIERT/ABLEITUNG/ANNAHME/TBD/KALIBRIERT) mitgeliefert wird.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

from .knowledge import PACKAGES, MENU, ANNAHME, ABLEITUNG, VERIFIZIERT, TBD
from .params import load_params, p
from .schema import EventFile


def choose_menu(veg_share: float, vegan_share: float, gf_count: int, n_sorts: int = 6) -> list[dict]:
    """Wählt bis zu n Sorten mit Begründung. Regel: mindestens 1 vegane, 2 vegetarische,
    2 mit Fleisch/Fisch; bei glutenfrei-Bedarf bevorzugt gf-mögliche Sorten."""
    by_id = {m["id"]: m for m in MENU}
    picks = []

    def add(mid, why):
        if mid in by_id and all(x["id"] != mid for x in picks):
            picks.append({**by_id[mid], "why": why})

    add("margarita", "Klassiker, vegetarisch, glutenfrei möglich – höchste Akzeptanz")
    add("marinera", "vegan und glutenfrei möglich – deckt Vegan + Zöliakie ab")
    add("pepperoni", "beliebte Fleischsorte, glutenfrei möglich")
    if vegan_share >= 0.15:
        add("verde", f"veganer Anteil {vegan_share:.0%} – zweite vegane Sorte")
    if veg_share >= 0.4:
        add("champinon", f"vegetarischer Anteil {veg_share:.0%} – dritte vegetarische Sorte, gf möglich")
    add("diavola", "scharfe Fleischsorte für Abwechslung")
    add("champinon", "vegetarisch, glutenfrei möglich")
    add("formaggi", "vegetarisch, käsebetont")
    add("atun", "Fisch-Option, glutenfrei möglich")
    picks = picks[:n_sorts]
    if gf_count > 0 and sum(1 for x in picks if x["gf_possible"]) < 3:
        picks = [x for x in picks if x["gf_possible"]][:n_sorts]
    return picks


def distribute_pizzas(total: int, menu: list[dict], veg_share: float, vegan_share: float) -> list[dict]:
    """Verteilt Pizzen auf Sorten proportional zu Ernährungsanteilen (deterministisch)."""
    vegan = [m for m in menu if m["vegan"]]
    veg_only = [m for m in menu if m["vegetarian"] and not m["vegan"]]
    meat = [m for m in menu if not m["vegetarian"]]
    n_vegan = round(total * vegan_share)
    n_veg = round(total * max(veg_share - vegan_share, 0))
    n_meat = total - n_vegan - n_veg
    out = []
    for group, n in ((vegan, n_vegan), (veg_only, n_veg), (meat, n_meat)):
        if not group:
            continue
        base, rest = divmod(n, len(group))
        for i, m in enumerate(group):
            out.append({"id": m["id"], "name": m["name"], "pizzas": base + (1 if i < rest else 0),
                        "vegan": m["vegan"], "vegetarian": m["vegetarian"]})
    # Falls Gruppen fehlen (z.B. keine Fleischsorte), Rest auf erste Sorte
    diff = total - sum(o["pizzas"] for o in out)
    if out and diff:
        out[0]["pizzas"] += diff
    return out


def plan(ev: EventFile, package: str | None = None, params: dict | None = None) -> dict:
    params = params or load_params()
    pkg_key = (package or ev.package or "classic").lower()
    pkg = PACKAGES[pkg_key]
    guests = ev.guests or 0
    assumptions = []

    veg = ev.veg_share if ev.veg_share is not None else p(params, "default_veg_share")
    if ev.veg_share is None:
        assumptions.append(f"veg_share={veg:.0%} ({params['default_veg_share']['status']})")
    vegan = ev.vegan_share if ev.vegan_share is not None else p(params, "default_vegan_share")
    if ev.vegan_share is None:
        assumptions.append(f"vegan_share={vegan:.0%} ({params['default_vegan_share']['status']})")
    vegan = min(vegan, veg) if veg else vegan
    gf = ev.gf_count if ev.gf_count is not None else round(guests * p(params, "default_gf_share"))
    if ev.gf_count is None:
        assumptions.append(f"glutenfrei={gf} Gäste ({params['default_gf_share']['status']})")

    pizzas_pp = pkg["pizzas_pp"]
    buffer = p(params, "safety_buffer")
    pizzas_base = math.ceil(guests * pizzas_pp)
    pizzas_total = math.ceil(pizzas_base * (1 + buffer))
    menu = choose_menu(veg, vegan, gf)
    distribution = distribute_pizzas(pizzas_total, menu, veg, vegan)

    dough_g = p(params, "dough_g_per_pizza")
    dough_kg = pizzas_total * dough_g / 1000
    flour_kg = dough_kg * p(params, "flour_share_of_dough")
    water_l = dough_kg * p(params, "water_share_of_dough")
    salt_g = flour_kg * p(params, "salt_g_per_kg_flour")
    cheese_pizzas = sum(d["pizzas"] for d in distribution if not d["vegan"])
    sauce_kg = pizzas_total * p(params, "sauce_g_per_pizza") / 1000
    cheese_kg = cheese_pizzas * p(params, "cheese_g_per_pizza") / 1000
    toppings_kg = pizzas_total * p(params, "topping_g_per_pizza") / 1000
    gf_doughballs = math.ceil(gf * pizzas_pp * (1 + buffer)) if gf else 0

    shopping = [
        {"item": "Mehl Tipo 00", "qty": round(flour_kg, 1), "unit": "kg", "formula": "Pizzen × Teigling × Mehlanteil", "status": params["dough_g_per_pizza"]["status"]},
        {"item": "Wasser", "qty": round(water_l, 1), "unit": "l", "formula": "Pizzen × Teigling × Wasseranteil", "status": params["water_share_of_dough"]["status"]},
        {"item": "Salz", "qty": round(salt_g / 1000, 2), "unit": "kg", "formula": "Mehl × Salz/kg", "status": params["salt_g_per_kg_flour"]["status"]},
        {"item": "Tomatensauce / San Marzano", "qty": round(sauce_kg, 1), "unit": "kg", "formula": "Pizzen × Sauce/Pizza", "status": params["sauce_g_per_pizza"]["status"]},
        {"item": "Fior di Latte", "qty": round(cheese_kg, 1), "unit": "kg", "formula": "Käse-Pizzen × Käse/Pizza", "status": params["cheese_g_per_pizza"]["status"]},
        {"item": "Beläge gesamt (Sortenmix)", "qty": round(toppings_kg, 1), "unit": "kg", "formula": "Pizzen × Belag/Pizza", "status": params["topping_g_per_pizza"]["status"]},
        {"item": "Glutenfreie Teiglinge", "qty": gf_doughballs, "unit": "Stk", "formula": "gf-Gäste × Pizzen p.P. × Puffer", "status": "ABLEITUNG"},
    ]
    if pkg["antipasti"]:
        shopping.append({"item": "Antipasti-Mix", "qty": round(guests * p(params, "antipasti_g_per_guest") / 1000, 1), "unit": "kg",
                         "formula": "Gäste × Antipasti/Gast", "status": params["antipasti_g_per_guest"]["status"]})
    if pkg["dessert"]:
        shopping.append({"item": "Dessert-Portionen (Tiramisu/Panna Cotta)", "qty": math.ceil(guests * p(params, "dessert_portions_per_guest")), "unit": "Stk",
                         "formula": "Gäste × Portion/Gast", "status": params["dessert_portions_per_guest"]["status"]})

    # Personal
    helpers = max(p(params, "min_helpers"), math.ceil(guests / p(params, "guests_per_helper")))
    serving_h = pkg["serving_hours"]
    travel_h = (2 * (ev.distance_km or 10) / p(params, "travel_speed_kmh"))
    onsite_h = (p(params, "setup_min") + p(params, "preheat_min") + p(params, "teardown_min")) / 60 + serving_h
    hours_per_helper = round(onsite_h + travel_h, 1)

    # Ofenkapazität
    oven_ph = p(params, "oven_pizzas_per_hour")
    needed_ph = pizzas_total / serving_h if serving_h else 0
    capacity_ok = needed_ph <= oven_ph
    capacity_note = (f"Bedarf {needed_ph:.0f} Pizzen/h vs. Kapazität {oven_ph}/h ({params['oven_pizzas_per_hour']['status']}). "
                     + ("OK." if capacity_ok else "ENGPASS – längere Servierzeit, Vorbacken oder zweiter Ofen nötig."))

    # Zeitplan
    timeline = build_timeline(ev, params, serving_h)
    countdown = build_countdown(ev, pizzas_total, flour_kg)

    return {
        "package": pkg_key, "package_name": pkg["name"], "guests": guests,
        "pizzas_pp": pizzas_pp, "pizzas_pp_status": pkg["pizzas_pp_status"],
        "pizzas_base": pizzas_base, "buffer": buffer, "pizzas_total": pizzas_total,
        "veg_share": veg, "vegan_share": vegan, "gf_count": gf,
        "menu": [{"id": m["id"], "name": m["name"], "why": m["why"], "vegan": m["vegan"], "vegetarian": m["vegetarian"], "gf_possible": m["gf_possible"]} for m in menu],
        "distribution": distribution,
        "dough_kg": round(dough_kg, 1), "shopping": shopping,
        "staff": {"helpers": helpers, "hours_per_helper": hours_per_helper, "formula": "max(min_helpers, ceil(Gäste / Gäste_pro_Helfer)); Stunden = Aufbau+Vorheizen+Service+Abbau+Fahrt",
                  "status": params["guests_per_helper"]["status"]},
        "equipment": ["Steinofen-Anhänger", "Holz (Menge TBD)", "Teigkühlung / Teigboxen", "Arbeitstisch + Mehl", "Pizzaschieber (2)",
                      "Servierbretter" if pkg_key != "classic" else "Pappteller & Servietten", "Gasflasche/Zündhilfe (falls genutzt)",
                      "Feuerlöscher", "Erste-Hilfe", "Allergen-Aushang (freigegebene Version)", "Wetterschutz/Pavillon (bei Outdoor)"],
        "oven": {"pizzas_per_hour": oven_ph, "needed_per_hour": round(needed_ph, 1), "ok": capacity_ok, "note": capacity_note},
        "timeline": timeline, "countdown": countdown, "assumptions": assumptions,
        "params_used": {k: params[k] for k in ["dough_g_per_pizza", "safety_buffer", "oven_pizzas_per_hour", "guests_per_helper", "setup_min", "preheat_min", "teardown_min"]},
    }


def build_timeline(ev: EventFile, params: dict, serving_h: float) -> list[dict]:
    start = ev.serving_start or "18:00"
    base = datetime.strptime(start, "%H:%M")
    setup = p(params, "setup_min"); preheat = p(params, "preheat_min"); teardown = p(params, "teardown_min")
    travel_min = round(60 * (ev.distance_km or 10) / p(params, "travel_speed_kmh"))
    t_arrive = base - timedelta(minutes=setup + preheat)
    t_leave = t_arrive - timedelta(minutes=travel_min)
    t_end = base + timedelta(hours=serving_h)
    rows = [
        (t_leave, "Abfahrt Bremen (Anhänger angekuppelt, Checkliste abgehakt)", "Fahrer"),
        (t_arrive, "Ankunft, Anhänger positionieren, Ofen anfeuern", "Team"),
        (t_arrive + timedelta(minutes=setup), "Aufbau fertig, Teig temperieren, Stationen einrichten", "Team"),
        (base - timedelta(minutes=15), "Ofen auf Temperatur, erste Testpizza", "Pizzaiolo"),
        (base, f"Servierbeginn ({serving_h:g} h)", "Team"),
        (t_end, "Servierende, Abbau beginnt", "Team"),
        (t_end + timedelta(minutes=teardown), "Abbau fertig, Abfahrt", "Team"),
    ]
    note = "Servierbeginn aus Anfrage" if ev.serving_start else "Servierbeginn 18:00 ANGENOMMEN"
    return [{"time": t.strftime("%H:%M"), "task": task, "owner": owner, "note": note if i == 4 else ""} for i, (t, task, owner) in enumerate(rows)]


def build_countdown(ev: EventFile, pizzas_total: int, flour_kg: float) -> list[dict]:
    return [
        {"t": "T-48h", "task": f"Einkauf finalisieren (Mehl {flour_kg:.0f} kg, Käse, Beläge), Allergen-Aushang drucken (nur freigegebene Version)"},
        {"t": "T-36h", "task": f"Teig ansetzen: {pizzas_total} Teiglinge (lange Führung)"},
        {"t": "T-24h", "task": "Kunde: Gästezahl, Zufahrt, Strom, Wetterschutz final bestätigen; Team-Einsatzbrief senden"},
        {"t": "T-12h", "task": "Holz, Equipment-Checkliste, Kühlung, Feuerlöscher prüfen; Anhänger packen"},
        {"t": "T-6h", "task": "Beläge vorbereiten und kühlen, Käse portionieren"},
        {"t": "T-3h", "task": "Abfahrt laut Zeitplan; Wetter-Check; Kundenkontakt Ankunftszeit"},
        {"t": "T-0", "task": "Servierbeginn; Pizza Pulse starten (optional)"},
        {"t": "T+1 Tag", "task": "Waste Lens: Restmengen wiegen, Ist-Zahlen erfassen, Lern-Loop füttern"},
    ]
