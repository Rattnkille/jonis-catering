"""Angebots- und Antwortentwürfe im JONIS-Ton sowie mehrsprachige Menüschilder.

Ton: herzlich, handwerklich, direkt, süditalienisch. Kein 'Holzofen', immer 'Steinofen'.
Keine Gedankenstriche. Preise nur aus knowledge.PACKAGES (VERIFIZIERT, ab-Preise).
"""
from __future__ import annotations

from .knowledge import PACKAGES, FACTS, COMPANY
from .schema import EventFile

def _de_date(iso: str) -> str:
    try:
        y, m, d = iso.split("-")
        return f"{int(d):02d}.{int(m):02d}.{y}"
    except Exception:  # noqa: BLE001
        return iso


TYPE_LABEL = {"hochzeit": "eure Hochzeit", "firmenevent": "euer Firmenevent", "privat": "eure Feier", None: "euer Event"}


def offer_variants(ev: EventFile) -> list[dict]:
    guests = ev.guests or 0
    billing_guests = max(guests, 50) if guests else 0
    out = []
    for key in ("classic", "event", "premium"):
        pkg = PACKAGES[key]
        total = billing_guests * pkg["price_pp_brutto"]
        fit = []
        if ev.budget_pp and pkg["price_pp_brutto"] > ev.budget_pp:
            fit.append(f"über Budget p.P. ({ev.budget_pp:.0f} €)")
        if ev.budget_total and total > ev.budget_total:
            fit.append(f"über Gesamtbudget ({ev.budget_total:.0f} €)")
        if ev.event_type == "hochzeit" and key == "classic":
            fit.append("für Hochzeiten meist Event oder Premium empfohlen (Antipasti/Dessert)")
        out.append({
            "package": key, "name": pkg["name"], "price_pp_brutto": pkg["price_pp_brutto"], "price_status": pkg["price_status"],
            "billing_guests": billing_guests, "total_brutto_ab": round(total, 2),
            "note_min": ("Mindestgröße 50 Personen: Berechnung unter 50 ist TBD (Geschäftsentscheidung)" if guests and guests < 50 else ""),
            "includes": pkg["includes"], "fit_notes": fit,
            "travel_note": "Anfahrt bis 10 km um Bremen inklusive, darüber Fahrtkostenpauschale (Betrag TBD)",
            "status": "ENTWURF – 'ab'-Preise laut Website, individuelle Kalkulation und Freigabe nötig",
        })
    return out


def response_draft(ev: EventFile, recommended: str = "event") -> str:
    pkg = PACKAGES[recommended]
    what = TYPE_LABEL.get(ev.event_type)
    guests = f"{ev.guests} Gäste" if ev.guests else "eure Gästezahl"
    when = f"am {_de_date(ev.date)}" if ev.date else "an eurem Wunschtermin"
    where = f" in {ev.location}" if ev.location else ""
    lines = [
        "Hallo [NAME],",
        "",
        f"danke für eure Anfrage für {what} {when}{where}. Das klingt nach einem schönen Anlass für Pizza aus dem Steinofen.",
        "",
        f"Für {guests} passt aus unserer Sicht unser {pkg['name']}-Paket am besten: {', '.join(pkg['includes'][:3])}. "
        f"Preislich liegt das ab {pkg['price_pp_brutto']:.0f} € pro Person, inklusive Auf- und Abbau und Servicepersonal.",
        "",
    ]
    if ev.questions:
        n = {1: "noch eine Sache", 2: "noch zwei Dinge", 3: "noch drei Dinge"}[len(ev.questions)]
        lines.append(f"Damit wir sauber planen können, brauchen wir {n} von euch:")
        for q in ev.questions:
            lines.append(f"- {q}")
        lines.append("")
    if ev.allergen_mentions:
        lines.append("Zu Allergien: Schickt uns bitte die genauen Angaben schriftlich. Wir arbeiten mit einer geprüften Zutatenliste und sagen euch ehrlich, was geht und was nicht.")
        lines.append("")
    lines += [
        "Wenn das passt, schicken wir euch ein konkretes Angebot. Mit einer Anzahlung von 10 % ist der Termin fest reserviert.",
        "",
        "Herzliche Grüße aus Bremen",
        "Joni von JONIS Catering",
    ]
    return "\n".join(lines)


SIGN_I18N = {
    "Tomatensauce": {"en": "tomato sauce", "it": "salsa di pomodoro"},
    "San-Marzano-Tomaten": {"en": "San Marzano tomatoes", "it": "pomodori San Marzano"},
    "Knoblauch": {"en": "garlic", "it": "aglio"}, "Oregano": {"en": "oregano", "it": "origano"},
    "Olivenöl": {"en": "olive oil", "it": "olio d'oliva"}, "Fior di Latte": {"en": "fior di latte", "it": "fior di latte"},
    "Basilikum": {"en": "basil", "it": "basilico"}, "Champignons": {"en": "mushrooms", "it": "champignon"},
    "Trüffelöl": {"en": "truffle oil", "it": "olio al tartufo"}, "Petersilie": {"en": "parsley", "it": "prezzemolo"},
    "scharfe Salami": {"en": "spicy salami", "it": "salame piccante"}, "Chilihonig": {"en": "chili honey", "it": "miele al peperoncino"},
    "Thunfisch": {"en": "tuna", "it": "tonno"}, "rote Zwiebeln": {"en": "red onions", "it": "cipolla rossa"},
    "Kapern": {"en": "capers", "it": "capperi"}, "'Nduja": {"en": "'nduja", "it": "'nduja"},
    "süße Paprika": {"en": "sweet peppers", "it": "peperoni dolci"}, "Honig": {"en": "honey", "it": "miele"},
    "Gorgonzola": {"en": "gorgonzola", "it": "gorgonzola"}, "Parmesan": {"en": "parmesan", "it": "parmigiano"},
    "Ricotta": {"en": "ricotta", "it": "ricotta"}, "Rucola": {"en": "rocket", "it": "rucola"},
    "Salami Piccante": {"en": "salami piccante", "it": "salame piccante"}, "Chili": {"en": "chili", "it": "peperoncino"},
    "Zucchini": {"en": "courgette", "it": "zucchine"}, "Paprika": {"en": "peppers", "it": "peperoni"},
    "Pilze": {"en": "mushrooms", "it": "funghi"}, "Artischocken": {"en": "artichokes", "it": "carciofi"},
    "Kräuter": {"en": "herbs", "it": "erbe"},
}
TAGS = {"vegan": {"de": "vegan", "en": "vegan", "it": "vegano"}, "vegetarian": {"de": "vegetarisch", "en": "vegetarian", "it": "vegetariano"},
        "spicy": {"de": "scharf", "en": "spicy", "it": "piccante"}, "gf": {"de": "glutenfrei möglich", "en": "gluten-free on request", "it": "senza glutine su richiesta"}}


def menu_signs(menu: list[dict], allergen_report: dict, langs=("de", "en", "it")) -> list[dict]:
    from .knowledge import MENU
    by_id = {m["id"]: m for m in MENU}
    rows_by_name = {r["pizza"]: r for r in allergen_report["rows"]}
    signs = []
    for m in menu:
        full = by_id[m["id"]]
        tags = [k for k in ("vegan", "vegetarian", "spicy") if full.get(k)] + (["gf"] if full["gf_possible"] else [])
        if "vegan" in tags and "vegetarian" in tags:
            tags.remove("vegetarian")
        alle = rows_by_name.get(full["name"], {})
        per_lang = {}
        for lang in langs:
            ings = [i if lang == "de" else SIGN_I18N.get(i, {}).get(lang, i) for i in full["ingredients"]]
            allergen_line = ("Allergene: " + ", ".join(alle.get("allergens", [])) + " (ENTWURF, nicht freigegeben)") if not alle.get("matrix_approved") else "Allergene: " + ", ".join(alle.get("allergens", []))
            per_lang[lang] = {"title": full["name"], "ingredients": ", ".join(ings), "tags": ", ".join(TAGS[t][lang] for t in tags), "allergens": allergen_line}
        signs.append({"id": m["id"], "langs": per_lang, "release_blocked": alle.get("release_blocked", True)})
    return signs


def team_brief(ev: EventFile, pl: dict, risks: list[dict]) -> str:
    lines = [f"EINSATZBRIEF {ev.event_id} " + ("(SYNTHETISCHE DEMO)" if ev.synthetic else ""),
             f"Event: {ev.event_type or 'unbekannt'} | Datum: {ev.date or 'TBD'} | Ort: {ev.location or 'TBD'} | Gäste: {pl['guests']} | Paket: {pl['package_name']}",
             f"Pizzen geplant: {pl['pizzas_total']} (Basis {pl['pizzas_base']} + Puffer {pl['buffer']:.0%}) | Teig: {pl['dough_kg']} kg",
             f"Team: {pl['staff']['helpers']} Personen à {pl['staff']['hours_per_helper']} h", "",
             "ZEITPLAN"] + [f"  {t['time']}  {t['task']}  [{t['owner']}]" for t in pl["timeline"]] + ["", "SORTEN & MENGEN"] + \
            [f"  {d['pizzas']:>3}  {d['name']}" for d in pl["distribution"]] + ["", "RISIKEN & MASSNAHMEN"] + \
            [f"  [{r['level']}] {r['risk']} -> {r['measure']}" for r in risks] + \
            ["", "ALLERGENE: Nur der freigegebene Aushang gilt. Bei Nachfrage: Zutatenliste zeigen, nichts versprechen.",
             "NOTFALL: Feuerlöscher am Anhänger, Erste-Hilfe-Set, Notrufnummer 112. Verantwortlich: Einsatzleitung (TBD Name)."]
    return "\n".join(lines)
