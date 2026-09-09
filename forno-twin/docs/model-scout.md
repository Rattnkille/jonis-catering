# Modell-Scout und Entscheidungsmatrix (Phase 3)

Geprüft am 2026-09-09 über die Hugging-Face-Hub-API (Model-Card-Metadaten). Qualität auf JONIS-Testfällen konnte in der Remote-Umgebung **nicht** gemessen werden, weil `huggingface.co` per Netzwerkrichtlinie blockiert ist (HTTP 403 am Egress-Proxy). Die Spalte „Qualität“ ist daher offen und wird vom Loop auf Jonis Mac nachgetragen (Backlog B5/B8).

## Speech-to-Text (Sprachmemo)

| Kriterium | Baseline `openai/whisper-tiny` | Kandidat `primeline/whisper-large-v3-turbo-german` |
|---|---|---|
| Lizenz | Apache-2.0 | Apache-2.0 |
| Parameter | 37,8 M | 808,9 M |
| Sprache | multilingual, de mittelmäßig | de spezialisiert |
| RAM (geschätzt, fp32 CPU) | ~0,5 GB | ~3,5 GB |
| Latenz 60-s-Memo, CPU (Erwartung) | Sekunden | Minuten auf CPU, ok auf Apple Silicon |
| Aktualität | 2024-02 | 2024-12 |
| Datenschutz | lokal | lokal |
| Offline | ja | ja |
| Integrationsaufwand | `transformers` pipeline | identisch |
| Qualität JONIS-Memos | **offen** | **offen** |
| Entscheidung | Start (Smoke Test) | Kandidat, wenn Baseline WER > 15 % |

## Retrieval (Wissensbasis)

| Kriterium | `paraphrase-multilingual-MiniLM-L12-v2` | `intfloat/multilingual-e5-small` | `Qwen/Qwen3-Embedding-0.6B` |
|---|---|---|---|
| Lizenz | Apache-2.0 | MIT | Apache-2.0 |
| Parameter | 117,7 M | 117,7 M | 595,8 M |
| Sprache | 50+ inkl. de | 90+ inkl. de | multilingual |
| RAM | ~0,5 GB | ~0,5 GB | ~2,5 GB |
| Offline | ja | ja | ja |
| Entscheidung | Baseline | Alternative (aktueller, MIT) | nur bei belegtem Qualitätsgewinn |

Fallback ohne Modell: lexikalische Wortüberlappung (`hf_models.lexical_retrieve`), im Pilot aktiv.

## Zero-Shot-Triage

| Kriterium | Regelbasis (`extract.classify_event_type`) | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` |
|---|---|---|
| Lizenz | – | MIT |
| Parameter | 0 | 278,8 M |
| Genauigkeit auf 15 Testfällen | 15/15 (event_type) | offen |
| Laufzeit | < 1 ms | ~1 s CPU |
| Aktualität | – | 2024-01 |
| Entscheidung | **aktiv** | optionaler Hinweis (`use_hf`), kein Faktensetzer |

## Bild/Video (Location Scout)

`HuggingFaceTB/SmolVLM2-500M-Video-Instruct` (Apache-2.0, 507 M, Prompts auf Englisch). Nur Hinweise zu Zufahrt, Stellfläche, Wetterschutz, jeder Hinweis „zu bestätigen“. Food-101 (`ethz/food101`) bewusst nicht verwendet: keine JONIS-Wahrheitsquelle, Lizenz laut Prompt unklar.

## Regel

Kleinstes Modell, das die Qualitätsgrenze erreicht. Solange keine Messung existiert, bleibt die deterministische Regelbasis die Produktionslogik.
