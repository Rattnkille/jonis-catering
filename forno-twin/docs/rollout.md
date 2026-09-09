# Rolloutplan

## 7 Tage

| Tag | Schritt | Ergebnis |
|---|---|---|
| 1 | Auf dem Mac: `cd forno-twin && make setup && make run`. Demo SYN-001 durchklicken. | Cockpit läuft lokal |
| 1 | Konflikte klären: Telefonnummer, Öffnungszeiten in schema.org | zwei Entscheidungen |
| 2 | Allergen-Matrix mit Lieferantenspezifikationen prüfen; `approved_by`/`approved_at` setzen, `verified` je Zutat | Menüschilder freigabefähig |
| 3 | Eine echte (pseudonymisierte) Anfrage durch `python -m forno_twin run anfrage.txt` laufen lassen; Rückfragen und Antwortentwurf bewerten | erster Realtest |
| 4 | `pip install -r requirements-ml.txt`; ASR-Smoke-Test mit einem eigenen 60-s-Memo (whisper-tiny), Ergebnis in Backlog B5 | Sprachmemo-Eingang bewertet |
| 5 | Parameter prüfen: Teigling, Sauce, Käse, Puffer in `data/parameters.json` (ANNAHME → eigene Werte) | Mengen realistischer |
| 6-7 | Nächstes Event: Ofenleistung messen, Restmengen wiegen, Ist-JSON anlegen | erstes Ist-Datenset |

## 30 Tage

1. Zwei Events mit Ist-Daten → `make calibrate` → Parameter KALIBRIERT (Ofen, Gäste/Helfer, Puffer).
2. Loop-Routine 4 Läufe: Backlog B3, B4, B7 erledigt; Eval-Set auf 20+ Fälle.
3. Entscheidung Zero-Shot-Triage: nur wenn Regelbasis auf realen Anfragen < 90 % Trefferquote.
4. Pizza Pulse einmal live testen (Strichliste am Tablet), Erkenntnis in Sortenwahl übernehmen.
5. Falls > 30 reale Anfragen vorliegen: Retrieval-Wissensbasis mit MiniLM/e5 lokal aktivieren und gegen lexikalischen Fallback messen.
6. Kein Training, solange die Regelbasis die Qualitätsgrenze hält.
