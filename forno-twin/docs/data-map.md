# Datenlandkarte

| Quelle | Eigentümer | Sensibilität | Aktualität | Benötigte Felder | Erlaubter Verarbeitungsort |
|---|---|---|---|---|---|
| `llms.txt` (Repo) | JONIS | öffentlich | 2026-09-09 geprüft | Pakete, Preise, Menü, Region, Ablauf | überall |
| `index.html` (Website) | JONIS | öffentlich | 2026-09-09 geprüft | FAQ, schema.org (Konflikte: Telefon, Öffnungszeiten) | überall |
| `kalkulation.html` (intern) | JONIS | intern | Standardwerte, kein Datum | Formeln, Defaults (ANNAHME) | lokal / Repo (noindex) |
| Kundenanfragen (E-Mail, Formular, Memo) | Kunde / JONIS | personenbezogen | laufend | Datum, Gäste, Ort, Zeit, Budget, Ernährung, Allergiehinweise | nur lokal, pseudonymisiert; nie in öffentliche Modelle/Spaces |
| Ist-Daten nach Event (`data/actuals/`) | JONIS | Betriebsgeheimnis | je Event | Mengen, Restmengen, Personalstunden, Zeiten | lokal; nicht committen (gitignore) |
| Allergen-Matrix | JONIS + Lieferanten | Lebensmittelsicherheit | Entwurf 0.1 | Zutat → EU-Allergene, verified, Freigabe | lokal / Repo nach Freigabe |
| Synthetische Events | erzeugt 2026-09-09 | keine (erfunden) | statisch | Testfälle, expected | überall, als synthetisch markiert |
| HF Model Cards | Hugging Face / Autoren | öffentlich | via Hub-API 2026-09-09 | Lizenz, Größe, Sprache | Metadaten überall; Gewichte nur lokal |
| Gmail/Kalender (bestehende Routinen) | JONIS | personenbezogen | live | nicht vom FORNO TWIN gelesen | außerhalb dieses Piloten |

Erfolgsmessung (definiert in Phase 0): Zeit bis Angebotsentwurf (Pipeline: < 0,1 s, Mensch: Freigabe), Vollständigkeit Eventakte (Ø 84 % auf Testfällen), Rückfragequalität (max. 3, priorisiert), Halluzinationsrate (0 durch deterministische Regeln; Modelle nur Hinweise), kritische Allergenfehler (0), Mengenabweichung (erst mit Ist-Daten messbar), Laufzeit (Ø 3 ms), Kosten (0 €), geschätzte Zeitersparnis siehe `docs/roi.md`.
