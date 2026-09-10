"""Ort und grobe Entfernung ab Bremen (Backlog B4).

Datenlage ehrlich halten:
- Postleitzahl -> Ort ist eine ABLEITUNG aus einer kleinen, manuell gepflegten Tabelle
  der Orte, die die JONIS-Website als Einzugsgebiet nennt (llms.txt, index.html FAQ).
- Die Entfernungen sind grobe Schätzwerte (Status ANNAHME) und ersetzen keine
  Routenberechnung. Vor jeder Fahrtkostenrechnung prüfen.
- Straßenadressen werden bewusst NICHT als Ort übernommen, sondern pseudonymisiert.
"""
from __future__ import annotations

import re
from typing import Optional

DISTANCE_STATUS = "ANNAHME"
DISTANCE_NOTE = "grobe Schätzung ab Bremen-Mitte, keine Routenberechnung"

# (PLZ-Bereich von, bis, Ort, geschätzte Straßenentfernung ab Bremen in km)
PLZ_TABLE = [
    (28195, 28779, "Bremen", 8),
    (27749, 27755, "Delmenhorst", 15),
    (28816, 28816, "Stuhr", 12),
    (28844, 28844, "Weyhe", 15),
    (28832, 28832, "Achim", 20),
    (28876, 28876, "Oyten", 15),
    (28865, 28865, "Lilienthal", 15),
    (28857, 28857, "Syke", 25),
    (27711, 27711, "Osterholz-Scharmbeck", 25),
    (27777, 27777, "Ganderkesee", 25),
    (27283, 27283, "Verden", 40),
    (26121, 26135, "Oldenburg", 50),
]

CITY_DISTANCE = {row[2]: row[3] for row in PLZ_TABLE}

STREET_RE = re.compile(
    r"\b([A-ZÄÖÜ][a-zäöüß-]{2,}(?:straße|strasse|str\.|weg|allee|platz|damm|ring|gasse|chaussee))\s*(\d+\s*[a-zA-Z]?)",
    re.UNICODE)
PLZ_RE = re.compile(r"\b(\d{5})\b")


def plz_lookup(plz: int) -> Optional[tuple[str, int]]:
    for lo, hi, city, km in PLZ_TABLE:
        if lo <= plz <= hi:
            return city, km
    return None


def find_plz(text: str) -> Optional[tuple[int, Optional[str], Optional[int]]]:
    """Erste Postleitzahl im Text plus Ort und geschätzte Entfernung, falls bekannt."""
    for m in PLZ_RE.finditer(text):
        plz = int(m.group(1))
        if not 1000 <= plz <= 99999:
            continue
        hit = plz_lookup(plz)
        if hit:
            return plz, hit[0], hit[1]
        return plz, None, None
    return None


def distance_for_city(city: Optional[str]) -> Optional[int]:
    return CITY_DISTANCE.get(city) if city else None
