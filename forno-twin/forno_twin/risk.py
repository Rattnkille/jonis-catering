"""Risiko-, Engpass- und Notfallcheck (regelbasiert)."""
from __future__ import annotations

from datetime import date

from .schema import EventFile


def assess(ev: EventFile, pl: dict, today: date | None = None) -> list[dict]:
    today = today or date.today()
    risks = []

    def add(level, risk, measure, source="Regel"):
        risks.append({"level": level, "risk": risk, "measure": measure, "source": source})

    if not pl["oven"]["ok"]:
        add("HOCH", "Ofenkapazität unter Bedarf (Parameter TBD)", "Servierzeit verlängern, Teil vorbacken oder zweiter Ofen; Kapazität real messen")
    if ev.location_type in ("outdoor", "gemischt") and not ev.weather_protection:
        add("HOCH", "Outdoor ohne bestätigten Wetterschutz", "Pavillon mitnehmen, Kunde nach überdachtem Platz fragen, Wetter-Check T-3h")
    if ev.power_available is False:
        add("MITTEL", "Kein Strom vor Ort", "Batteriebeleuchtung/Akku-Kühlung prüfen; Kühlkette mit Kühlboxen sichern")
    elif ev.power_available is None:
        add("NIEDRIG", "Strom ungeklärt", "Bei Bestätigung abfragen (Kühlung, Licht)")
    if not any("Zufahrt" in n for n in ev.access_notes):
        add("MITTEL", "Zufahrt/Stellplatz für Anhänger unbekannt", "Kunde um Foto/Beschreibung der Zufahrt bitten (Location Scout)")
    if ev.allergen_mentions:
        add("HOCH", f"Allergie-Hinweise: {', '.join(ev.allergen_mentions)}", "Schriftliche Bestätigung; nur freigegebene Matrix; betroffene Gäste persönlich ansprechen")
    if ev.gf_count and ev.gf_count > 0:
        add("MITTEL", f"{ev.gf_count} glutenfreie Gäste", "Separate Teiglinge, separater Schieber, Kontamination vermeiden; 'auf Anfrage' laut Website")
    if ev.guests and ev.guests < 50:
        add("MITTEL", "Unter Mindestgröße 50", "Geschäftsentscheidung: Mindestberechnung oder Absage")
    if ev.guests and ev.guests > 150:
        add("MITTEL", "Über 150 Gäste (Website: Firmenevents ideal 50-150)", "Zweiten Pizzaiolo und ggf. zweiten Ofen prüfen")
    if ev.date:
        try:
            weeks = (date.fromisoformat(ev.date) - today).days / 7
            if 0 <= weeks < 4:
                add("MITTEL", f"Kurzer Vorlauf ({weeks:.1f} Wochen)", "Einkauf und Personal sofort sichern")
        except ValueError:
            pass
    if ev.distance_km and ev.distance_km > 50:
        add("MITTEL", "Außerhalb 50-km-Radius", "Fahrtkostenpauschale (TBD) und Zeitpuffer klären")
    if ev.veg_share and ev.veg_share >= 0.5:
        add("NIEDRIG", "Hoher vegetarischer Anteil", "Mindestens 3 vegetarische + 2 vegane Sorten; Pizza Pulse aktiv nutzen")
    if ev.security_findings:
        add("HOCH", "Sicherheitsauffälligkeit im Eingabedokument", "Inhalt manuell prüfen; keine automatischen Aktionen; Absender verifizieren")
    if ev.conflicts:
        add("MITTEL", f"{len(ev.conflicts)} Konflikt(e) in der Eventakte", "Vor Angebot klären: " + " | ".join(ev.conflicts)[:200])
    add("INFO", "Notfallplan Standard", "Feuerlöscher, Erste Hilfe, Ersatz-Gas/Holz, Ersatzhelfer-Liste (TBD), Kundennummer vor Ort")
    return risks
