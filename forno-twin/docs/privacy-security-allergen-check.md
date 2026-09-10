# Datenschutz-, Security- und Allergen-Risikocheck

Stand 2026-09-09. Prüfer: Pilot-Session (KI), Freigabe durch Joni ausstehend.

## Datenschutz

| Prüfpunkt | Ergebnis | Beleg |
|---|---|---|
| PII wird vor Verarbeitung pseudonymisiert | ja (E-Mail, Telefon, Namen nach Grußformeln, Straßenadressen) | `extract.pseudonymize`, Tests SYN-011 und SYN-017 |
| PII verlässt den Rechner | nein; keine Netzwerkaufrufe in der Pipeline | `pipeline.py` ohne HTTP; `hf_models` nur bei `use_hf` und nur Modell-Download |
| Exporte frei von Klarnamen | ja | `test_full_demo_exports` |
| Ist-Daten nicht im Repo | ja | `.gitignore` `data/actuals/*.json` |
| Straßenadressen | werden erkannt und durch `[ADRESSE_n]` ersetzt, nie als Ort übernommen | `geo.STREET_RE`, `TestGeo::test_street_is_pseudonymized` |
| Postleitzahl | bleibt erhalten (kein Personenbezug ohne Hausnummer) und liefert Ort plus grobe Entfernung | `geo.find_plz`, Status ANNAHME |
| Grenzen | Namen ohne Grußformel und ungewöhnliche Telefonformate können durchrutschen; deshalb bleibt Sichtprüfung vor jedem Teilen | Tab 2 |

## Security

| Prüfpunkt | Ergebnis |
|---|---|
| Prompt-Injection in Dokumenten | erkannt, markiert, blockiert Auto-Freigabe; Anweisungen werden nie ausgeführt (Test SYN-010) |
| Secrets | keine im Code, in Logs oder Docs; HF_TOKEN nur als Umgebungsvariable; `hf_whoami` liefert keine Token-Werte |
| Öffentliche Veröffentlichung | nichts veröffentlicht: keine HF-Repos, Spaces, Jobs; `forno-twin/**` vom FTP-Deploy der Website ausgeschlossen (`deploy.yml`) |
| Abhängigkeiten | Kern ohne Fremdpakete; UI: gradio; Tests: pytest |
| Gradio-Bindung | nur `127.0.0.1:7861`, kein `share=True` |
| GitHub Actions | `contents: write` nur für Berichte im Repo; keine Secrets nötig |

## Allergene und Lebensmittelsicherheit

| Regel | Umsetzung |
|---|---|
| Allergene nur aus freigegebener Matrix | `allergens.py`; Matrix-Status „ENTWURF – NICHT FREIGEGEBEN“ |
| Ein ungeprüfter Allergen-Fakt = kritischer Fehler | `release_blocked=True`, Eval-Metrik `allergen_critical_errors` muss 0 sein |
| Modelle liefern nur Hinweise | `check_mentions` → Status HINWEIS; Bild/Audio setzen nie Allergene |
| Menüschilder zeigen Entwurfsstatus | „(ENTWURF, nicht freigegeben)“ in allen Sprachen |
| Kreuzkontamination glutenfrei | Risiko-Check: separate Teiglinge, separater Schieber; Website sagt „auf Anfrage“ |
| Offene Punkte | Lieferantenspezifikationen für Salami, 'Nduja, Kapern, Artischocken, Trüffelöl prüfen (Milch/Senf/Sellerie/Sulfite möglich) |

## Restrisiken

1. Kostenwerte sind Rechner-Standardwerte; eine falsche Preisentscheidung ist möglich, wenn das Band ignoriert wird. Gegenmaßnahme: Freigabeschritt „Kalkulation“.
2. Ofenkapazität ist TBD; Engpass-Alarme sind derzeit Annahmen. Gegenmaßnahme: Messung (CHECKPOINT nächster Schritt).
3. Die KI-Routine schreibt Code. Gegenmaßnahme: nur Draft-PRs, Tests und Allergen-Metrik als Schranke, keine Website-Änderungen.
