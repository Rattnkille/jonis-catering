# Architektur und Datenfluss

```
Eingaben (Text, E-Mail, PDF-Text, Transkript, optional Audio/Foto)
        │
        ▼
[extract.py]  Pseudonymisierung → Injection-Check → Regelextraktion → Eventakte (schema.py)
        │            ▲
        │            └── optional: hf_models.zero_shot_triage (nur Hinweis)
        ▼
[allergens.py]  Matrix laden → Allergene je Pizza → release_blocked, solange nicht freigegeben
        ▼
[planning.py]  Sortenwahl → Pizzen/Teig/Einkauf → Personal → Ofenkapazität → Zeitplan → Countdown
        ▼
[calc.py]      Prime-Cost-Formeln aus kalkulation.html → Unsicherheitsband → Freigabe nötig
        ▼
[offer.py]     3 Varianten, Antwortentwurf (JONIS-Ton), Menüschilder DE/EN/IT, Einsatzbrief
        ▼
[risk.py]      Risiko-, Engpass-, Notfallcheck
        ▼
[simulator.py] 3 Störungen: Plan + Kalkulation neu, Vorher/Nachher-Diff
        ▼
[export.py]    JSON / CSV / XLSX / HTML / TXT  →  out/
        ▼
[app.py]       Gradio-Cockpit (7 Tabs)   |   [__main__.py] CLI

Nach dem Event:
[learn.py]  Ist-Daten (data/actuals/*.json) → Waste Lens → calibrate() → data/calibration.json
[params.py] parameters.json + calibration.json → Planungsparameter mit Status
[pulse.py]  anonyme Stimmen → nächste Charge

Loop:
loop/improve.sh → Tests → eval/run_eval.py → learn.calibrate → loop/report.py → docs/loop-status.md
GitHub Actions (sonntags + bei Push) und Claude-Routine (wöchentlich, Draft-PR)
```

## Rollen ChatGPT/Claude und Hugging Face

- **Orchestrator (ChatGPT/Claude):** versteht die Anfrage im Kontext, plant Schritte, formuliert Kunden- und Teamtexte, prüft Ergebnisse. Im Pilot ist der Orchestrator der Loop-Lauf (Routine) und die Person am Cockpit. Die Pipeline selbst braucht kein LLM.
- **Maschinenhalle (Hugging Face):** Modelle für Sprache (ASR), Retrieval (Embeddings), Triage (Zero-Shot), Bildhinweise (VLM). Immer als Hinweisgeber mit Status HINWEIS. Registry mit Lizenzstand in `hf_models.REGISTRY`.
- **Deterministischer Kern:** Mengen, Kosten, Personal, Allergene, Zeiten. Nie aus einem Modell.

## Datenschutz-by-Design

- Pseudonymisierung vor jedem weiteren Schritt; Mapping nur im Prozessspeicher.
- Betriebsdaten (Gäste, Mengen, Zeiten) getrennt von PII (Schema).
- Keine Netzwerkaufrufe außer optionalem Modell-Download vom HF Hub (lokal, wenn `use_hf`).
- Exporte enthalten keine Klarnamen (Test `test_full_demo_exports`).
