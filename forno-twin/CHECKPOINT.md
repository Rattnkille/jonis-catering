# CHECKPOINT – JONIS FORNO TWIN

Stand: 2026-09-10 (Session 1: Masterprompt durchlaufen; erster Verbesserungslauf erledigt)

## Status

| Phase | Stand |
|---|---|
| 0 Audit | erledigt: Quellen (llms.txt, index.html, kalkulation.html), HF-Login (OAuth, read/jobs/contribute), Hardware (4 CPU, 15 GB RAM, kein GPU), 2 Quellenkonflikte gefunden |
| 1 Portfolio | erledigt: 8 Anwendungsfälle bewertet, Flaggschiff FORNO TWIN, 2 Quick Wins, 1 Überraschung (docs/opportunities.md) |
| 2 Datenvertrag | erledigt: Schema v1.0.0, 15 synthetische Events, Allergen-Matrix (Entwurf), Wissensbasis |
| 3 Modell-Scout | erledigt als Entscheidungsmatrix; lokale Inferenz in Remote-Umgebung blockiert (huggingface.co 403 durch Netzwerkrichtlinie) |
| 4 Pilot | erledigt: Gradio-App mit 7 Ansichten, CLI, Exporte, Screenshot-Prüfung |
| 5 Evaluation | erledigt: 32 Tests grün, 129/129 Eval-Prüfungen über 18 Testfälle, 0 Allergenfehler |
| 6 Training | bewusst nicht: keine gemessene Baseline-Lücke, keine echten Daten. Training-ready Schema + Eval-Set vorhanden |
| 7 Betriebsreife | Doku vollständig (docs/), Loop aktiv: GitHub-Workflow (sonntags + Push) und Claude-Routine `trig_01VZeB5f9TJVuCrzv6wein2v` (dienstags 05:23 UTC, ohne Connector-Zugriffe: pusht Branch, öffnet keinen PR) |

## Befehle

```bash
cd forno-twin && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -m pytest tests -q && python eval/run_eval.py && python app.py
bash loop/improve.sh
```

## Links

- Draft-PR: https://github.com/Rattnkille/jonis-catering/pull/19
- Branch: `claude/masterprompt-self-improving-loop-lf5ycf`
- Loop-Branch der Routine: `claude/forno-twin-loop`

## Artefakte

- Code: `forno_twin/` (16 Module), `app.py`, `tests/test_engine.py`, `eval/run_eval.py`, `loop/`
- Daten: `data/synthetic_events.json` (18 Fälle), `data/allergen_matrix.json`, `data/parameters.json`, `data/calibration.json`
- Demo-Exporte: `out/demo/SYN-001_*` (lokal erzeugt, nicht committet)
- Screenshots: `docs/screenshot-*.png`

## Erster Verbesserungslauf (2026-09-10, im Repo statt per Routine)

Drei Backlog-Punkte mit Owner "Loop" erledigt, Genauigkeit unverändert 100 %:

- **B3 Zahlwörter** (`forno_twin/numbers.py`): "achtzig bis hundert Personen", "zwei Dutzend Leute", "fünfundsechzig Gäste". Testfälle SYN-016, SYN-018.
- **B4 PLZ und Entfernung** (`forno_twin/geo.py`): Postleitzahl liefert Ort und eine grobe Entfernung ab Bremen (Status ANNAHME). Straßenadressen werden jetzt pseudonymisiert statt ignoriert. Testfall SYN-017.
- **B7 PDF-Eingang** (`forno_twin/ingest.py`): PDF-Text ohne Pflicht-Fremdpaket (zlib-Fallback), `pypdf` wird bevorzugt, wenn installiert. `python -m forno_twin run anfrage.pdf` läuft durch.

Neue Backlog-Punkte daraus: B9 (Entfernungen gegen echte Routen prüfen), B10 (Scan-PDF ohne Textebene sichtbar machen), B11 (Uhrzeit-Zahlwörter).

## Offene Tests

- ASR-Vergleich whisper-tiny vs. primeline turbo german auf deutschen Memos (Hub-Zugang nötig)
- Zero-Shot-Triage mDeBERTa auf 15 Fällen vs. Regelbasis (Hub-Zugang nötig)
- Location Scout mit SmolVLM2 auf Demo-Foto (Hub-Zugang nötig)

## Exakt nächster Schritt

Joni entscheidet **eine** Sache: Ofenkapazität am nächsten Event messen (Pizzen pro Stunde über 60 Minuten Vollbetrieb) und in `data/actuals/<event>.json` eintragen. Damit wird der wichtigste TBD-Parameter real, und der Engpass-Alarm hört auf zu raten.

Der nächste Loop-Lauf nimmt Backlog-Punkt B9 (Entfernungen gegen echte Routen prüfen).
