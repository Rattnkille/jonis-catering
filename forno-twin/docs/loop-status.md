# FORNO TWIN – Loop-Status

Letzter Lauf: 2026-09-09T13:09:20+00:00

## Kennzahlen des letzten Laufs

- Genauigkeit Einzelprüfungen: **100.0%** (Δ +0.0% zum Vorlauf)
- Testfälle vollständig bestanden: **15/15**
- Kritische Allergenfehler: **0** (muss 0 sein)
- Ø Vollständigkeit Eventakte: 84%
- Fehlgeschlagen: keine

## Verlauf (letzte 10 Läufe)

| Zeit | Genauigkeit | Fälle ok | Allergenfehler |
|---|---|---|---|
| 2026-09-09T13:04:37+00:00 | 98.1% | 13/15 | 0 |
| 2026-09-09T13:05:06+00:00 | 100.0% | 15/15 | 0 |
| 2026-09-09T13:09:10+00:00 | 100.0% | 15/15 | 0 |
| 2026-09-09T13:09:20+00:00 | 100.0% | 15/15 | 0 |

## Kalibrierung aus Ist-Daten

- Reale Events mit Ist-Daten: **0**
- Überschriebene Parameter: keine (Parameter bleiben ANNAHME)
- Nur 0 reale Events mit Ist-Daten (Minimum 2). Keine Kalibrierung, Parameter bleiben ANNAHME.

## Verbesserungs-Backlog (priorisiert)

1. [offen] **Ofenkapazität messen und als Parameter erfassen** – oven_pizzas_per_hour ist TBD; jeder Engpass-Alarm ist derzeit eine Annahme (Messgröße: Parameterstatus TBD -> KALIBRIERT)
2. [offen] **Allergen-Matrix mit Lieferantenspezifikationen prüfen und freigeben** – Blockiert jede automatische Freigabe von Menüschildern (Messgröße: allergen_matrix.approved_by gesetzt, verified=true je Zutat)
3. [offen] **Zahlwörter und Spannen in der Gäste-Extraktion ('zwei Dutzend', '80-100 Leute' bereits ok)** – Robustere Extraktion bei umgangssprachlichen Anfragen (Messgröße: neuer Testfall SYN-016 besteht)
4. [offen] **Straßenadressen und PLZ als Location erkennen, Entfernung ab Bremen schätzen** – Fahrtkostenlogik braucht Distanz; heute nur Ortsname (Messgröße: distance_km automatisch gesetzt bei PLZ/Ort)
5. [offen] **ASR-Smoke-Test mit echtem deutschen Sprachmemo (whisper-tiny vs. primeline turbo german)** – Sprachmemo-Eingang ist integriert, aber ungetestet (Hub in Remote-Umgebung blockiert) (Messgröße: WER auf 3 synthetischen Memos dokumentiert)
6. [offen] **Ist-Daten von 2 realen Events erfassen (data/actuals)** – Erst dann kalibriert der Lern-Loop Parameter (Messgröße: n_real_events >= 2)
7. [offen] **PDF-Eingang: Textextraktion (pypdf) vor der Extraktion** – Angebotsanfragen kommen teils als PDF (Messgröße: Testfall mit PDF-Fixture besteht)
8. [offen] **Location Scout: Bild-Hinweise (SmolVLM2) als Beobachtungen mit Status HINWEIS** – Bonusfunktion, nur nach ASR/Retrieval-Basis (Messgröße: 3 Hinweise auf Demo-Foto, jeweils als 'zu bestätigen' markiert)

## Regeln für den nächsten Loop-Lauf

1. Erst `bash loop/improve.sh`. Rote Tests oder Allergenfehler > 0 haben Vorrang vor allem anderen.
2. Genau einen Backlog-Punkt umsetzen, mit neuem Testfall in `data/synthetic_events.json` und Prüfung in `eval/run_eval.py`.
3. Genauigkeit darf nicht sinken. Sinkt sie, Änderung zurücknehmen.
4. Keine Preise, Kosten, Allergene oder Kapazitäten erfinden. Neue Parameter bekommen Status ANNAHME oder TBD.
5. Backlog in `loop/backlog.json` pflegen (erledigt markieren, neue Lücken aus Fehlerbeispielen ergänzen).
6. Änderungen als PR auf Branch `claude/forno-twin-loop` mit dem Loop-Bericht im PR-Text. Nichts veröffentlichen, keine Kundenkontakte, keine Bezahlkosten.
