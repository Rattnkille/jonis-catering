# Kostenjournal

| Zeit (UTC) | Aktion | Modell / Ressource | Geschätzte Kosten | Tatsächliche Kosten | Erwarteter Nutzen | Entscheidung |
|---|---|---|---|---|---|---|
| 2026-09-09 12:5x | Phase 0 Audit: Repo, HF-Login (whoami), Hardware | Claude-Session (Abo), HF-Connector (kostenlos) | 0 € | 0 € | Faktenbasis | durchgeführt |
| 2026-09-09 12:5x | Model-Card-Prüfung 7 Modelle | HF Hub API via Connector | 0 € | 0 € | Lizenz-/Größenklarheit | durchgeführt |
| 2026-09-09 12:5x | pip install torch/transformers/gradio (CPU) | PyPI, ~2,5 GB Disk | 0 € | 0 € | Adapter testbar | durchgeführt; Gewichte nicht ladbar (Hub 403) |
| 2026-09-09 13:0x | Engine, Tests, Eval, App gebaut und lokal ausgeführt | CPU, keine Modelle | 0 € | 0 € | Pilot | durchgeführt |
| 2026-09-09 13:1x | HF-Spaces-Smoke-Test (Zero-Shot/ASR) geprüft | HF Spaces | 0 € | 0 € | Modellhinweis | verworfen: Spaces exponieren keine passende Funktion bzw. brauchen öffentliche Upload-URL |
| 2026-09-09 13:1x | GitHub Actions Loop (wöchentlich) | GitHub Actions Minuten (Free Tier) | 0 € (~1 min/Lauf) | 0 € | Regression-Schutz, Berichte | eingerichtet |
| 2026-09-09 13:2x | Claude-Routine „FORNO TWIN Verbesserungslauf“ wöchentlich | Claude-Nutzung (Abo) | Abo-Kontingent, keine HF-Kosten | – | ein Backlog-Punkt pro Woche | eingerichtet; jederzeit pausierbar |
| offen | ASR-Test lokal auf Mac | whisper-tiny / primeline (lokal) | 0 € | – | Sprachmemo-Eingang | startklar, Freigabe nicht nötig |
| offen | Fine-Tuning | GPU | nicht geschätzt | – | kein belegter Bedarf | **nicht gestartet** |

Budgetregel: ChatGPT/Claude-Nutzung und Hugging-Face-Compute sind getrennt. Kein HF-Compute wurde genutzt. Kein kostenpflichtiger Endpoint, Job oder Space wurde angelegt.
