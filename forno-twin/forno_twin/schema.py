"""Versionierbares Event-Schema (Datenvertrag) für den FORNO TWIN.

PII (Name, E-Mail, Telefon, Adresse) wird strikt von Betriebsmerkmalen getrennt:
- `EventFile.contact` enthält nur pseudonymisierte Platzhalter.
- Betriebsdaten sind frei von personenbezogenen Daten und dürfen in
  Auswertungen, Evaluationen und Modell-Tests verwendet werden.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

SCHEMA_VERSION = "1.0.0"


@dataclass
class Claim:
    """Eine Aussage mit Status und Quelle (VERIFIZIERT / ABLEITUNG / ANNAHME / DEMO / TBD / KONFLIKT)."""
    value: Any
    status: str
    source: str = ""
    note: str = ""
    approved: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class EventFile:
    event_id: str
    schema_version: str = SCHEMA_VERSION
    synthetic: bool = True
    event_type: Optional[str] = None            # hochzeit | firmenevent | privat | unbekannt
    date: Optional[str] = None                  # ISO oder Teilangabe
    date_partial: Optional[str] = None
    location: Optional[str] = None
    location_type: Optional[str] = None         # indoor | outdoor | unbekannt
    distance_km: Optional[float] = None
    guests: Optional[int] = None
    guests_children: Optional[int] = None
    time_window: Optional[str] = None
    serving_start: Optional[str] = None
    budget_total: Optional[float] = None
    budget_pp: Optional[float] = None
    package: Optional[str] = None
    veg_share: Optional[float] = None
    vegan_share: Optional[float] = None
    gf_count: Optional[int] = None
    allergen_mentions: list = field(default_factory=list)   # nur Hinweise, nie Wahrheit
    dietary_notes: list = field(default_factory=list)
    power_available: Optional[bool] = None
    access_notes: list = field(default_factory=list)
    weather_protection: Optional[bool] = None
    language: str = "de"
    contact: dict = field(default_factory=dict)             # nur Pseudonyme
    raw_sources: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)
    gaps: list = field(default_factory=list)
    questions: list = field(default_factory=list)
    security_findings: list = field(default_factory=list)
    provenance: dict = field(default_factory=dict)          # feld -> Claim-Dict
    approvals: dict = field(default_factory=dict)           # schritt -> {approved, by, at}

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "EventFile":
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)


APPROVAL_STEPS = [
    ("eventakte", "Eventakte geprüft (Fakten, Konflikte, Lücken)"),
    ("allergene", "Allergen-Matrix freigegeben"),
    ("kalkulation", "Kalkulation und Preis geprüft"),
    ("angebot", "Angebotstext freigegeben"),
    ("einsatzplan", "Einsatzplan an Team freigegeben"),
]
