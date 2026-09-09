# CHECKPOINT – JONIS FORNO TWIN

Stand: 2026-09-09 (Session 1, Masterprompt vollständig durchlaufen)

## Status

| Phase | Stand |
|---|---|
| 0 Audit | erledigt: Quellen (llms.txt, index.html, kalkulation.html), HF-Login (OAuth, read/jobs/contribute), Hardware (4 CPU, 15 GB RAM, kein GPU), 2 Quellenkonflikte gefunden |
| 1 Portfolio | erledigt: 8 Anwendungsfälle bewertet, Flaggschiff FORNO TWIN, 2 Quick Wins, 1 Überraschung (docs/opportunities.md) |
| 2 Datenvertrag | erledigt: Schema v1.0.0, 15 synthetische Events, Allergen-Matrix (Entwurf), Wissensbasis |
| 3 Modell-Scout | erledigt als Entscheidungsmatrix; lokale Inferenz in Remote-Umgebung blockiert (huggingface.co 403 durch Netzwerkrichtlinie) |
| 4 Pilot | erledigt: Gradio-App mit 7 Ansichten, CLI, Exporte, Screenshot-Prüfung |
| 5 Evaluation | erledigt: 21 Tests grün, 104/104 Eval-Prüfungen, 0 Allergenfehler |
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

- Code: `forno_twin/` (13 Module), `app.py`, `tests/test_engine.py`, `eval/run_eval.py`, `loop/`
- Daten: `data/synthetic_events.json`, `data/allergen_matrix.json`, `data/parameters.json`, `data/calibration.json`
- Demo-Exporte: `out/demo/SYN-001_*` (lokal erzeugt, nicht committet)
- Screenshots: `docs/screenshot-*.png`

## Offene Tests

- ASR-Vergleich whisper-tiny vs. primeline turbo german auf deutschen Memos (Hub-Zugang nötig)
- Zero-Shot-Triage mDeBERTa auf 15 Fällen vs. Regelbasis (Hub-Zugang nötig)
- Location Scout mit SmolVLM2 auf Demo-Foto (Hub-Zugang nötig)

## Exakt nächster Schritt

Joni entscheidet **eine** Sache: Ofenkapazität am nächsten Event messen (Pizzen pro Stunde über 60 Minuten Vollbetrieb) und in `data/actuals/<event>.json` eintragen. Damit wird der wichtigste TBD-Parameter real, und der Engpass-Alarm hört auf zu raten.

Der Loop-Lauf nimmt danach Backlog-Punkt B3 (Zahlwörter in der Extraktion).
