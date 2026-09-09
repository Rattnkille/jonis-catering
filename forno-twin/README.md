# JONIS FORNO TWIN

Digitaler Event-Zwilling für JONIS Pizza Catering: von der chaotischen Kundenanfrage bis zum freigegebenen Einsatzplan und dem Lern-Loop nach dem Event.

**Grundsatz:** KI schlägt vor, deterministische Formeln rechnen, JONIS entscheidet. Jede kritische Zahl trägt einen Status: VERIFIZIERT, ABLEITUNG, ANNAHME, SYNTHETISCHE DEMO, TBD oder KONFLIKT.

## Ein-Befehl-Start

```bash
cd forno-twin
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # nur gradio, openpyxl, pytest
python app.py                            # Cockpit auf http://127.0.0.1:7861
```

Ohne UI:

```bash
python -m forno_twin demo                # kompletter Demo-Durchlauf, Exporte in out/demo/
python -m forno_twin demo SYN-010        # anderer synthetischer Fall
python -m forno_twin run anfrage.txt     # eigene Anfrage (Textdatei)
python -m pytest tests -q                # 21 Tests
python eval/run_eval.py                  # Evaluation über 15 Testfälle
bash loop/improve.sh                     # Verbesserungs-Loop (Tests, Eval, Kalibrierung, Bericht)
```

Optionale HF-Modelle (ASR, Zero-Shot, Embeddings): `pip install -r requirements-ml.txt`. Ohne diese Pakete läuft alles trotzdem, die Modell-Adapter melden dann sauber „nicht verfügbar“.

## Was drin ist

| Ansicht | Funktion | Modul |
|---|---|---|
| 1 Anfrage erfassen | Text, Transkript, Audio-/Bild-Eingang; Pseudonymisierung; Injection-Erkennung | `forno_twin/extract.py` |
| 2 Eventakte prüfen | Fakten mit Status, Konflikte, Lücken, max. 3 Rückfragen | `schema.py`, `extract.py` |
| 3 Menü & Kalkulation | Sortenwahl mit Begründung, Mengen, Prime-Cost-Formeln aus `kalkulation.html` | `planning.py`, `calc.py` |
| 4 Einkauf, Vorbereitung, Personal | Einkaufsliste, 48-h-Countdown, Zeitplan, Einsatzbrief | `planning.py`, `offer.py` |
| 5 Event-Simulator | +20 % Gäste, mehr vegetarisch/vegan, Regen + Verzögerung + Ausfall | `simulator.py` |
| 6 Lernen nach dem Event | Waste Lens (Plan vs. Ist), Pizza Pulse, Kalibrierung | `learn.py`, `pulse.py` |
| 7 Quellen & Freigaben | Freigabeschritte, Allergen-Status, Quellenkonflikte, Modellregister | `allergens.py`, `hf_models.py` |

Exporte pro Durchlauf: Eventakte JSON, Einkauf CSV + XLSX, Einsatzbrief HTML (druckbar), Antwortentwurf TXT.

## Dokumentation

- `CHECKPOINT.md` – Status, Befehle, nächster Schritt (für Fortsetzung)
- `docs/status.md` – Liste „Echt funktionsfähig / Demo / TBD / Benötigt Freigabe“
- `docs/architecture.md` – Architektur und Datenfluss
- `docs/data-dictionary.md` – Datenwörterbuch
- `docs/data-map.md` – Datenlandkarte (Quelle, Sensibilität, Verarbeitungsort)
- `docs/opportunities.md` – Chancenportfolio (Phase 1)
- `docs/model-scout.md` – Modellvergleich und Entscheidungsmatrix
- `docs/model-registry.md` – Modellregister mit Lizenz- und Versionsstand
- `docs/dataset-card.md` – Dataset Card der synthetischen Testdaten
- `docs/eval-report.md` – Evaluationsbericht (wird vom Loop aktualisiert)
- `docs/privacy-security-allergen-check.md` – Datenschutz-, Security- und Allergen-Risikocheck
- `docs/cost-journal.md` – Kostenjournal
- `docs/roi.md` – ROI-Abschätzung (drei Szenarien, klar als Annahme)
- `docs/rollout.md` – 7-Tage- und 30-Tage-Plan
- `docs/loop-status.md` – Stand des Verbesserungs-Loops

## Der selbstverbessernde Loop

1. **Deterministisch (kostenlos):** `.github/workflows/forno-twin-loop.yml` läuft sonntags und bei jedem Push in `forno-twin/`: Tests, Evaluation, Kalibrierung aus Ist-Daten, Bericht. Berichte werden committet.
2. **KI-Lauf (Claude Routine „FORNO TWIN Verbesserungslauf“, dienstags 05:23 UTC):** arbeitet `loop/IMPROVE_PROMPT.md` ab, erledigt genau einen Backlog-Punkt mit neuem Testfall und pusht auf `claude/forno-twin-loop`. Genauigkeit darf nicht sinken, Allergenfehler bleiben 0. Hinweis: Die Routine wurde ohne Connector-Zugriffe angelegt; sie kann pushen, aber keinen PR über die GitHub-Integration öffnen. Für automatische Draft-PRs die Routine in der claude.ai-Routinen-Ansicht mit GitHub verbinden, sonst den Branch manuell als PR öffnen. Pausieren jederzeit in der Routinen-Ansicht.
3. **Lernen aus Events:** Ist-Daten in `data/actuals/` (nicht committet) kalibrieren Ofenleistung, Gäste je Helfer und Puffer per gedämpftem EMA. Synthetische Daten kalibrieren nie.

## Sicherheitsregeln (fest eingebaut)

- Allergene nur aus `data/allergen_matrix.json`. Nicht freigegeben = Freigabe blockiert.
- Preise nur aus `knowledge.py` (Website-Stand 2026-09-09). Kosten sind Rechner-Standardwerte (ANNAHME).
- PII wird vor jeder Verarbeitung pseudonymisiert; nichts verlässt den Rechner.
- Prompt-Injection in Dokumenten wird erkannt, markiert und ignoriert.
- Keine öffentlichen Repos, Spaces, Kundenkontakte oder Bezahlkosten ohne Freigabe.
