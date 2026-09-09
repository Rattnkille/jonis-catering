"""Verifizierte Mini-Wissensbasis für JONIS (Stand 2026-09-09).

Quellen im Repo:
- llms.txt            (öffentliche Eckdaten, Pakete, Menü)
- index.html          (Website, FAQ, schema.org-Daten)
- kalkulation.html    (interner Prime-Cost-Rechner, Standardwerte)

Regel: Werte hier sind Fakten mit Quelle. Was nicht belegt ist, bleibt TBD.
"""
from __future__ import annotations

VERIFIZIERT = "VERIFIZIERT"
ABLEITUNG = "ABLEITUNG"
ANNAHME = "ANNAHME"
DEMO = "SYNTHETISCHE DEMO"
TBD = "TBD"
KONFLIKT = "KONFLIKT"

CHECK_DATE = "2026-09-09"


def fact(key, value, status, source, note=""):
    return {"key": key, "value": value, "status": status, "source": source,
            "checked": CHECK_DATE, "note": note}


# ---------------------------------------------------------------- Unternehmen
COMPANY = {
    "name": "Jonis Catering",
    "brand_line": "Neapolitanisches Pizza-Catering, live im Steinofen gebacken",
    "region": "Bremen und Umkreis von rund 50 km",
    "region_cities": ["Bremen", "Delmenhorst", "Stuhr", "Weyhe", "Achim", "Oyten",
                      "Lilienthal", "Verden", "Oldenburg", "Osterholz-Scharmbeck",
                      "Ganderkesee", "Syke"],
    "wording": {"oven": "Steinofen"},
}

FACTS = [
    fact("min_guests", 50, VERIFIZIERT, "llms.txt; index.html FAQ",
         "'Unser Catering ist ab 50 Personen buchbar.'"),
    fact("travel_included_km", 10, VERIFIZIERT, "index.html FAQ",
         "An- und Abfahrt im Umkreis von 10 km um Bremen inklusive."),
    fact("travel_flat_beyond", None, TBD, "index.html FAQ",
         "'darüber hinaus Fahrtkostenpauschale' – Höhe ist nirgends belegt."),
    fact("service_radius_km", 50, VERIFIZIERT, "llms.txt; index.html FAQ"),
    fact("response_time_h", 24, VERIFIZIERT, "index.html"),
    fact("lead_time_weeks", "4-6", VERIFIZIERT, "llms.txt; index.html FAQ"),
    fact("deposit_pct", 10, VERIFIZIERT, "llms.txt; index.html FAQ"),
    fact("favourite_pizzas_choice", 5, VERIFIZIERT, "llms.txt Ablauf",
         "'5 Favoriten-Pizzen wählen' (Flatrate aus 6 Sorten laut Paket) -> Konflikt 5 vs 6, siehe CONFLICTS"),
    fact("tone", "herzlich, handwerklich, direkt, süditalienisch, keine Verkaufssprache",
         VERIFIZIERT, "Masterprompt + Montags-Briefing-Routine ('immer Steinofen, nie Holzofen')"),
    fact("vat_pct", 19, ABLEITUNG, "kalkulation.html Standardwert (USt i.d.R. 19)",
         "Steuerliche Einordnung Catering vs. Lieferung nicht geprüft; ggf. 7 %/19 %-Frage."),
]

# ------------------------------------------------------------------- Pakete
PACKAGES = {
    "classic": {
        "name": "Classic", "price_pp_brutto": 27.0, "price_status": VERIFIZIERT,
        "source": "llms.txt; index.html (ab 27 € p.P.)",
        "pizzas_pp": 2.0, "pizzas_pp_status": VERIFIZIERT,
        "pizzas_pp_note": "'2 Pizzen p.P. aus 6 Sorten'",
        "serving_hours": 2.0, "antipasti": False, "dessert": False,
        "includes": ["Pizza-Flatrate aus 6 Sorten", "live im Steinofen", "2 Stunden Servierzeit",
                     "Pappteller & Servietten", "Auf- & Abbau", "Servicepersonal"],
    },
    "event": {
        "name": "Event", "price_pp_brutto": 37.0, "price_status": VERIFIZIERT,
        "source": "llms.txt; index.html (ab 37 € p.P., beliebteste Wahl)",
        "pizzas_pp": 2.5, "pizzas_pp_status": ABLEITUNG,
        "pizzas_pp_note": "Quelle sagt '2–3 Pizzen p.P.'; Mittelwert 2,5 als Planungsbasis",
        "serving_hours": 3.0, "antipasti": True, "dessert": False,
        "includes": ["Pizza-Flatrate aus 6 Sorten", "Antipasti-Platten als Empfang",
                     "3 Stunden Servierzeit", "Echtholz-Servierbretter", "Auf- & Abbau", "Servicepersonal"],
    },
    "premium": {
        "name": "Premium", "price_pp_brutto": 47.0, "price_status": VERIFIZIERT,
        "source": "llms.txt; index.html (ab 47 € p.P.)",
        "pizzas_pp": 2.5, "pizzas_pp_status": ANNAHME,
        "pizzas_pp_note": "Quelle nennt keine Pizzazahl für Premium; wie Event angesetzt",
        "serving_hours": 3.0, "antipasti": True, "dessert": True,
        "includes": ["erweiterte Antipasti-Auswahl", "Dessert (Tiramisu oder Panna Cotta)",
                     "individuelle Menü-Abstimmung", "Priorität bei Terminkonflikten",
                     "Auf- & Abbau", "Servicepersonal"],
    },
}

# --------------------------------------------------------------------- Menü
# Zutaten exakt laut llms.txt / schema.org-Menü. Diät-Tags laut Quelle.
MENU = [
    {"id": "marinera", "name": "La Marinera Noble", "ingredients": ["Tomatensauce", "Knoblauch", "Oregano", "Olivenöl"],
     "vegan": True, "vegetarian": True, "gf_possible": True, "spicy": False},
    {"id": "margarita", "name": "La Reina Margarita", "ingredients": ["San-Marzano-Tomaten", "Fior di Latte", "Basilikum"],
     "vegan": False, "vegetarian": True, "gf_possible": True, "spicy": False},
    {"id": "champinon", "name": "San Champiñón", "ingredients": ["Fior di Latte", "Champignons", "Trüffelöl", "Petersilie"],
     "vegan": False, "vegetarian": True, "gf_possible": True, "spicy": False},
    {"id": "pepperoni", "name": "La Guerrera OG Pepperoni", "ingredients": ["Fior di Latte", "scharfe Salami", "Chilihonig"],
     "vegan": False, "vegetarian": False, "gf_possible": True, "spicy": True},
    {"id": "atun", "name": "El Atún Valiente", "ingredients": ["Fior di Latte", "Thunfisch", "rote Zwiebeln", "Kapern"],
     "vegan": False, "vegetarian": False, "gf_possible": True, "spicy": False},
    {"id": "picante", "name": "La Picante Dulzura", "ingredients": ["Fior di Latte", "'Nduja", "süße Paprika", "Honig"],
     "vegan": False, "vegetarian": False, "gf_possible": False, "spicy": True},
    {"id": "formaggi", "name": "Quattro Formaggi", "ingredients": ["Fior di Latte", "Gorgonzola", "Parmesan", "Ricotta", "Rucola"],
     "vegan": False, "vegetarian": True, "gf_possible": False, "spicy": False},
    {"id": "diavola", "name": "La Diavola", "ingredients": ["San-Marzano-Tomaten", "Fior di Latte", "Salami Piccante", "Chili"],
     "vegan": False, "vegetarian": False, "gf_possible": False, "spicy": True},
    {"id": "verde", "name": "La Verde", "ingredients": ["Tomatensauce", "Zucchini", "Paprika", "Rucola", "Olivenöl"],
     "vegan": True, "vegetarian": True, "gf_possible": False, "spicy": False},
    {"id": "funghi_vegana", "name": "La Funghi Vegana", "ingredients": ["Tomatensauce", "Pilze", "Artischocken", "Kapern", "Kräuter"],
     "vegan": True, "vegetarian": True, "gf_possible": False, "spicy": False},
]
MENU_SOURCE = "llms.txt (Menü) + index.html schema.org MenuItem, Stand 2026-09-09"

# ------------------------------------------------------ Kalkulator-Standard
# Standardwerte aus kalkulation.html (Reset-Funktion). Es sind Rechner-Defaults,
# KEINE verifizierten Ist-Kosten. Status daher ANNAHME.
CALC_DEFAULTS = {
    "ware_pro_gast_netto": 9.0,
    "ware_pauschal": 50.0,
    "helfer": 2.5,
    "stunden_pro_helfer": 8.0,
    "stundenlohn": 15.0,
    "ag_pauschale_pct": 31.5,
    "fixkosten_anteil": 200.0,
    "minijob_grenze": 556.0,
}
CALC_DEFAULTS_STATUS = ANNAHME
CALC_DEFAULTS_SOURCE = "kalkulation.html resetForm() Standardwerte (Bezug: 80 Gäste, 27 € brutto)"

# ------------------------------------------------------------------ Konflikte
CONFLICTS = [
    {"topic": "Telefonnummer",
     "a": "+49 176 3237 0375 (llms.txt, Kontakt)",
     "b": "+4942168431162 (index.html schema.org 'telephone')",
     "action": "Nicht stillschweigend übernehmen. Joni bestätigt die kundenwirksame Nummer."},
    {"topic": "Öffnungszeiten",
     "a": "schema.org openingHoursSpecification: Di–Fr 11:00–15:00 (index.html)",
     "b": "Keine Öffnungszeiten im sichtbaren Text oder in llms.txt; Catering-Betrieb ohne Ladenlokal",
     "action": "Als veraltet/ungeklärt markieren. Nicht in Kundenkommunikation verwenden."},
    {"topic": "Sortenzahl",
     "a": "'Pizza-Flatrate aus 6 Sorten' (Pakete)",
     "b": "'5 Favoriten-Pizzen wählen' (Ablauf)",
     "action": "Planung nutzt 6 Sorten als Obergrenze; Kundentext nennt keine Zahl ohne Bestätigung."},
    {"topic": "Ofen-Wording",
     "a": "'Holzsteinofen / Pferdeanhänger' (Masterprompt)",
     "b": "'Steinofen' (Website, Routine: nie 'Holzofen')",
     "action": "Kundentexte verwenden ausschließlich 'Steinofen'."},
]

# --------------------------------------------------- Offene reale Datenlücken
OPEN_DATA = [
    "Wareneinsatz pro Pizza bzw. pro Person (Ist, nicht Rechner-Default)",
    "Personalbedarf und Personalkosten je Eventgröße (Ist)",
    "Energie-, Holz- und Fahrtkosten; Höhe der Fahrtkostenpauschale",
    "Aufbau-, Vorheiz-, Service- und Abbauzeiten (gemessen)",
    "Ofenkapazität: Pizzen pro Stunde (gemessen)",
    "Mindestumsatz und Berechnung bei < 50 Gästen",
    "Historische Plan/Ist-Mengen und Restmengen",
    "Verbindliche, freigegebene Zutaten- und Allergenmatrix",
]


def knowledge_snapshot() -> dict:
    return {"company": COMPANY, "facts": FACTS, "packages": PACKAGES, "menu": MENU,
            "menu_source": MENU_SOURCE, "calc_defaults": CALC_DEFAULTS,
            "calc_defaults_status": CALC_DEFAULTS_STATUS, "conflicts": CONFLICTS,
            "open_data": OPEN_DATA, "checked": CHECK_DATE}
