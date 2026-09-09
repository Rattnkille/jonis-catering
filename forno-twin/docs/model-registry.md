# Modellregister

Quelle: HF Hub API, abgerufen 2026-09-09 über den Hugging-Face-Connector. Keine Gewichte in dieser Umgebung geladen.

| Schlüssel | Modell-ID | Aufgabe | Lizenz | Parameter | Letztes Update | Status im Pilot |
|---|---|---|---|---|---|---|
| asr_baseline | openai/whisper-tiny | ASR | apache-2.0 | 37,8 M | 2024-02-29 | Adapter, ungetestet |
| asr_candidate | primeline/whisper-large-v3-turbo-german | ASR de | apache-2.0 | 808,9 M | 2024-12-03 | Adapter, ungetestet |
| embed_baseline | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | Embeddings | apache-2.0 | 117,7 M | 2026-01-28 | Adapter, lexikalischer Fallback aktiv |
| embed_alt | intfloat/multilingual-e5-small | Embeddings | mit | 117,7 M | 2026-04-02 | Adapter |
| embed_candidate | Qwen/Qwen3-Embedding-0.6B | Embeddings | apache-2.0 | 595,8 M | 2026-04-20 | Adapter |
| zeroshot_candidate | MoritzLaurer/mDeBERTa-v3-base-mnli-xnli | Zero-Shot | mit | 278,8 M | 2024-01-08 | Adapter (`use_hf`) |
| vision_candidate | HuggingFaceTB/SmolVLM2-500M-Video-Instruct | Bild/Video → Text | apache-2.0 | 507,5 M | 2025-04-08 | nur Registry (Backlog B8) |

Kommerzielle Nutzbarkeit: Apache-2.0 und MIT erlauben kommerzielle Nutzung mit Lizenzhinweis. Vor Produktivbetrieb Model Card erneut lesen (Nutzungshinweise, Bias, Sprachabdeckung).

HF-Konto: `PremJonathan` (OAuth, Scopes read-repos, jobs, contribute-repos, inference-api; kein Pro). Keine privaten Repos, Spaces oder Jobs angelegt. HF_TOKEN in dieser Umgebung nicht als Umgebungsvariable gesetzt (nur Connector-OAuth).
