# Datenwörterbuch (Schema v1.0.0)

## EventFile (Eventakte)

| Feld | Typ | Bedeutung | PII | Status-Quelle |
|---|---|---|---|---|
| event_id | str | Kennung | nein | intern |
| synthetic | bool | true = Demo-Daten | nein | intern |
| event_type | hochzeit / firmenevent / privat / null | Anlass | nein | ABLEITUNG (Schlüsselwörter) |
| date / date_partial | ISO / Text | Termin, Teilangabe | nein | VERIFIZIERT (Anfrage) oder TBD |
| location / location_type | str / indoor, outdoor, gemischt | Ort, Umgebung | nein* | Anfrage |
| distance_km | float | Entfernung ab Bremen | nein | ANNAHME aus PLZ/Ort-Tabelle (`geo.py`), von einer expliziten Angabe überschrieben |
| guests, guests_children | int | Gästezahl (bei Spanne: Maximum) | nein | Anfrage; KONFLIKT bei mehreren Werten |
| time_window, serving_start | str | Zeitfenster, Servierbeginn HH:MM | nein | Anfrage |
| budget_total, budget_pp | float | Budget gesamt / pro Person | nein | Anfrage |
| package | classic / event / premium | Paket | nein | Auswahl |
| veg_share, vegan_share | 0..1 | Anteile | nein | Anfrage oder ANNAHME (parameters.json) |
| gf_count | int | glutenfreie Gäste | nein | Anfrage oder ANNAHME |
| allergen_mentions | list | Rohhinweise aus Text | nein | HINWEIS, nie Wahrheit |
| dietary_notes | list | vegetarisch, vegan, glutenfrei, laktosefrei, halal, kein_schwein | nein | Anfrage |
| power_available, access_notes, weather_protection | bool / list / bool | Logistik | nein | Anfrage |
| language | de / en / it | Sprache der Anfrage | nein | Heuristik |
| contact | dict | nur Platzhalter [EMAIL_1], [TEL_1], [NAME_1], [ADRESSE_1] | Platzhalter | Pseudonymisierung |
| conflicts, gaps, questions | list | Widersprüche, Lücken, max. 3 Rückfragen | nein | Regeln |
| security_findings | list | Injection-Muster | nein | Regeln |
| provenance | dict | Feld → {status, source, note} | nein | Regeln |
| approvals | dict | Schritt → {approved, by, at, label} | nein | Mensch |

*Ortsname und Postleitzahl gelten allein als nicht personenbezogen; Straßenadressen werden erkannt und pseudonymisiert.

## Plan (planning.plan)

pizzas_base = ceil(Gäste × Pizzen p.P.); pizzas_total = ceil(pizzas_base × (1 + Puffer)); dough_kg = pizzas_total × Teigling / 1000; Einkauf je Zeile mit Formel und Parameterstatus; staff.helpers = max(min_helpers, ceil(Gäste / Gäste_pro_Helfer)); oven.needed_per_hour = pizzas_total / Servierstunden.

## Kalkulation (calc.calculate)

Exakt wie `kalkulation.html`: Umsatz netto = Gäste × Preis / 1,19; Ware = Gäste × Ware/Gast + Pauschale; Personal = Helfer × Stunden × Lohn × (1 + AG %); Prime Cost = Ware + Personal; Gewinn = Umsatz netto − Prime Cost − Fix. Band: Ware ±20 %, Personal ±15 % (ANNAHME).

## Ist-Daten (data/actuals/*.json)

Siehe `data/actuals/README.md`. Felder: guests_actual, pizzas_produced, leftover_pizzas, leftover_dough_kg, leftover_by_sort, helpers_actual, hours_per_helper_actual, serving_minutes_actual, weather, notes, synthetic.

## Parameter (data/parameters.json → data/calibration.json)

Jeder Parameter: value, status (ANNAHME / TBD / KALIBRIERT), note. Kalibrierung überschreibt nur value und setzt status KALIBRIERT mit Eventanzahl und Datum.
