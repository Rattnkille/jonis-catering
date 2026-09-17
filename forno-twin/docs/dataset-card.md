# Dataset Card: JONIS FORNO TWIN – synthetische Anfragen

**Datei:** `data/synthetic_events.json` · **Version:** 2026-09-09 · **Lizenz:** intern JONIS · **Status:** SYNTHETISCHE DEMO

## Zusammenfassung

15 erfundene Catering-Anfragen auf Deutsch, Englisch und Italienisch, die typische und schwierige Fälle für JONIS abdecken. Jeder Fall enthält `expected`-Werte für die Evaluation.

## Abdeckung

| Kategorie | Fälle |
|---|---|
| Normalfall (Hochzeit, Firmenevent) | SYN-001, SYN-002 |
| Unvollständig / Spam | SYN-003, SYN-015 |
| Unter Mindestgröße | SYN-004 |
| Widersprüchliche Angaben | SYN-005, SYN-001 (Memo) |
| Mehrsprachig | SYN-006 (en), SYN-007 (it) |
| Allergene unklar | SYN-008, SYN-001 |
| Knappes Budget | SYN-009 |
| Prompt-Injection im Dokument | SYN-010 |
| Datenschutzfalle (PII) | SYN-011 |
| Großevent / Ofenengpass | SYN-012 |
| Kurzer Vorlauf | SYN-013 |
| Hoher veg/vegan-Anteil | SYN-014 |

## Erzeugung

Manuell geschrieben am 2026-09-09 auf Basis der öffentlichen JONIS-Angebotslogik (Pakete, Region, Mindestgröße). Namen, E-Mails, Telefonnummern und Adressen sind erfunden (`example.org`, `example.com`, Musterweg). Keine echten Kunden, Buchungen oder Messwerte.

## Grenzen

- Keine echten Audio-Dateien; Sprachmemo als Transkript-Text.
- Keine Verteilung realer Anfragen; Anteile sind nicht repräsentativ.
- Nicht für Training gedacht; Eval-Set. Für Fine-Tuning wären mindestens 200 reale, pseudonymisierte Anfragen mit Train/Val/Test-Split nötig (Phase 6, nicht gestartet).

## Datenschutz

Keine personenbezogenen Daten. Darf lokal, im Repo und in Tests verwendet werden. Nicht als „JONIS-Daten“ nach außen kommunizieren.
