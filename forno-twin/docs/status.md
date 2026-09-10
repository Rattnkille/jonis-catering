# Status: Echt funktionsfähig / Demo / TBD / Benötigt Freigabe

Stand 2026-09-09. Jeder Punkt mit Beleg (Pfad, Test oder Log).

## Echt funktionsfähig (lokal getestet)

| Funktion | Beleg |
|---|---|
| Extraktion Anfrage → Eventakte (Datum, Gäste, Ort, Zeit, Budget, Ernährungsanteile, Konflikte, Lücken, max. 3 Rückfragen) | `tests/test_engine.py::TestExtraction` (9 Tests), `eval/run_eval.py` 129/129 |
| Deutsche Zahlwörter als Gästezahl ("achtzig bis hundert Personen", "zwei Dutzend Leute", "fünfundsechzig") | `TestNumberWords` (4 Tests), SYN-016, SYN-018 |
| Postleitzahl → Ort und grobe Entfernung ab Bremen (Status ANNAHME); unbekannte PLZ wird als Hinweis markiert | `TestGeo` (4 Tests), SYN-017 |
| PDF-Anfragen einlesen (zlib-Fallback ohne Fremdpaket, `pypdf` optional) | `TestPdfIngest` (4 Tests) |
| Pseudonymisierung von E-Mail, Telefon, Namen und Straßenadresse vor Verarbeitung | `test_pii_pseudonymized`, `TestGeo::test_street_is_pseudonymized`, SYN-011, SYN-017 |
| Prompt-Injection-Erkennung, keine Übernahme in Angebotstext | `test_prompt_injection_flagged`, SYN-010 |
| Mehrsprachige Anfragen (DE/EN/IT) | `test_multilingual`, SYN-006/007 |
| Deterministische Mengenplanung (Pizzen, Teig, Mehl, Wasser, Salz, Sauce, Käse, Beläge, gf-Teiglinge, Antipasti, Dessert) | `test_plan_formulas` |
| Kalkulation exakt nach `kalkulation.html`-Formeln inkl. Prime Cost, Minijob-Hinweis, Unsicherheitsband | `test_calc_matches_kalkulation_html_defaults` |
| Drei Angebotsvarianten mit Budget-Fit | `test_budget_fit` |
| Antwortentwurf im JONIS-Ton (Steinofen, Du-Form, keine Gedankenstriche) | `test_signs_marked_draft`, `out/demo/SYN-001_antwort.txt` |
| Menüschilder DE/EN/IT mit Diät-Tags | `test_signs_marked_draft` |
| Zeitplan, 48-h-Countdown, Einsatzbrief (HTML druckbar) | `test_full_demo_exports` |
| Simulator: +20 % Gäste, mehr veg/vegan, Regen + 30 min + Ausfall | `test_simulations`, Screenshot `docs/screenshot-5-simulator.png` |
| Risiko-, Engpass-, Notfallcheck | `test_big_event_bottleneck` |
| Allergen-Matrix blockiert Freigabe bis zur Prüfung | `TestAllergensSafety` (3 Tests) |
| Waste Lens (Plan vs. Ist) und Kalibrierung per EMA, synthetische Daten kalibrieren nie | `test_waste_lens_and_calibration_guard` |
| Pizza Pulse (anonyme Präferenzen → nächste Charge) | `test_pulse` |
| Exporte JSON, CSV, XLSX, HTML, TXT | `test_full_demo_exports` |
| Gradio-Cockpit mit 7 Ansichten im JONIS-Stil | `docs/screenshot-*.png` (Playwright, 2026-09-09) |
| Verbesserungs-Loop (Tests, Eval, Kalibrierung, Bericht) | `bash loop/improve.sh`, `docs/loop-status.md`, `eval/history.jsonl` |

## Demo (synthetisch, klar gekennzeichnet)

- 18 synthetische Events in `data/synthetic_events.json` (Namen, Kontakte, Orte erfunden)
- Sprachmemo-Eingang als Transkript-Text simuliert (SYN-001), weil ASR-Gewichte hier nicht ladbar waren
- Kostenwerte: Rechner-Standardwerte aus `kalkulation.html`, keine Ist-Kosten

## TBD (reale Daten fehlen)

- Ofenkapazität (Pizzen/h), Aufbau-/Vorheiz-/Abbauzeiten
- Entfernungen je Ort: grobe Schätzwerte in `forno_twin/geo.py`, nicht gegen echte Routen geprüft
- Wareneinsatz pro Pizza, Personalkosten, Energie/Holz, Fahrtkostenpauschale
- Mindestberechnung unter 50 Gästen
- Historische Plan/Ist-Mengen
- Zutaten-/Allergenmatrix mit Lieferantenspezifikation

## Benötigt Freigabe (Joni)

- Allergen-Matrix (`data/allergen_matrix.json`: `approved_by`, `approved_at`, `verified` je Zutat)
- Kundenwirksame Telefonnummer (Konflikt llms.txt vs. schema.org)
- Öffnungszeiten in schema.org (veraltet?)
- Jede Kundenkommunikation, jeder Preis, jeder Einsatzplan (Freigabeschritte in der Eventakte)
- Wöchentliche KI-Routine darf weiterlaufen (Claude-Nutzung, keine HF-Kosten)

## Vorbereitet, aber in dieser Umgebung nicht testbar

- HF-Modelle lokal (whisper-tiny, primeline turbo german, mDeBERTa, MiniLM, e5-small, Qwen3-Embedding, SmolVLM2): Adapter in `forno_twin/hf_models.py`, Registry mit Lizenzstand. Grund: `huggingface.co` ist aus der Remote-Umgebung per Netzwerkrichtlinie blockiert (HTTP 403 am Proxy). Auf Jonis Mac mit `pip install -r requirements-ml.txt` direkt nutzbar.
