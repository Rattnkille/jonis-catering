"""Hugging-Face-Adapter: optionale Modelle als Hinweisgeber, nie als Wahrheitsquelle.

Alle Funktionen sind fehlertolerant: fehlen Bibliotheken, Gewichte oder Netz,
kommt {"available": False, "reason": ...} zurück und die Pipeline läuft weiter.
HF_TOKEN wird ausschließlich aus der Umgebung gelesen, nie geloggt.
"""
from __future__ import annotations

import os
import time
from functools import lru_cache

# Modellregister: Kandidaten, Lizenzstand laut Model Card (geprüft 2026-09-09 via HF Hub API).
REGISTRY = {
    "asr_baseline": {"id": "openai/whisper-tiny", "task": "automatic-speech-recognition", "license": "apache-2.0",
                     "params_m": 37.8, "lang": "multilingual (de ok, geringere Qualität)", "checked": "2026-09-09"},
    "asr_candidate": {"id": "primeline/whisper-large-v3-turbo-german", "task": "automatic-speech-recognition", "license": "apache-2.0",
                      "params_m": 808.9, "lang": "de", "checked": "2026-09-09", "updated": "2024-12-03"},
    "embed_baseline": {"id": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "task": "sentence-similarity",
                       "license": "apache-2.0", "params_m": 117.7, "lang": "multilingual", "checked": "2026-09-09"},
    "embed_alt": {"id": "intfloat/multilingual-e5-small", "task": "sentence-similarity", "license": "mit", "params_m": 117.7,
                  "lang": "multilingual", "checked": "2026-09-09"},
    "embed_candidate": {"id": "Qwen/Qwen3-Embedding-0.6B", "task": "feature-extraction", "license": "apache-2.0", "params_m": 595.8,
                        "lang": "multilingual", "checked": "2026-09-09"},
    "zeroshot_candidate": {"id": "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli", "task": "zero-shot-classification", "license": "mit",
                           "params_m": 278.8, "lang": "multilingual (de)", "checked": "2026-09-09", "updated": "2024-01-08"},
    "vision_candidate": {"id": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct", "task": "image-text-to-text", "license": "apache-2.0",
                         "params_m": 507.5, "lang": "en (Prompts auf Englisch)", "checked": "2026-09-09"},
}


def _hf_token_present() -> bool:
    return bool(os.environ.get("HF_TOKEN"))


def status() -> dict:
    out = {"hf_token_env_present": _hf_token_present(), "libs": {}}
    for lib in ("torch", "transformers", "sentence_transformers", "gradio"):
        try:
            mod = __import__(lib)
            out["libs"][lib] = getattr(mod, "__version__", "ok")
        except Exception as e:  # noqa: BLE001
            out["libs"][lib] = f"fehlt ({type(e).__name__})"
    out["hub_reachable"] = hub_reachable()
    return out


@lru_cache(maxsize=1)
def hub_reachable(timeout: float = 5.0) -> bool:
    try:
        import urllib.request
        req = urllib.request.Request("https://huggingface.co/api/models/openai/whisper-tiny", method="HEAD")
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:  # noqa: BLE001
        return False


def _unavailable(reason: str, model: str) -> dict:
    return {"available": False, "reason": reason, "model": model}


def zero_shot_triage(text: str, labels=None, model_key: str = "zeroshot_candidate") -> dict:
    labels = labels or ["Hochzeit", "Firmenevent", "private Feier", "Spam oder unklar"]
    model = REGISTRY[model_key]["id"]
    try:
        from transformers import pipeline  # type: ignore
    except Exception as e:  # noqa: BLE001
        return _unavailable(f"transformers fehlt: {e}", model)
    if not hub_reachable():
        return _unavailable("huggingface.co nicht erreichbar (Netzwerkrichtlinie) – Gewichte können nicht geladen werden", model)
    t0 = time.time()
    try:
        clf = pipeline("zero-shot-classification", model=model)
        res = clf(text[:2000], candidate_labels=labels, hypothesis_template="Diese Anfrage ist {}.")
        return {"available": True, "model": model, "labels": res["labels"], "scores": [round(s, 3) for s in res["scores"]],
                "latency_s": round(time.time() - t0, 2), "role": "Hinweis (Triage), setzt keine Fakten"}
    except Exception as e:  # noqa: BLE001
        return _unavailable(f"Laden/Inferenz fehlgeschlagen: {type(e).__name__}: {e}", model)


def transcribe(audio_path: str, model_key: str = "asr_baseline") -> dict:
    model = REGISTRY[model_key]["id"]
    try:
        from transformers import pipeline  # type: ignore
    except Exception as e:  # noqa: BLE001
        return _unavailable(f"transformers fehlt: {e}", model)
    if not hub_reachable():
        return _unavailable("huggingface.co nicht erreichbar (Netzwerkrichtlinie)", model)
    t0 = time.time()
    try:
        asr = pipeline("automatic-speech-recognition", model=model)
        res = asr(audio_path, generate_kwargs={"language": "german"} if "whisper" in model else {})
        return {"available": True, "model": model, "text": res.get("text", ""), "latency_s": round(time.time() - t0, 2)}
    except Exception as e:  # noqa: BLE001
        return _unavailable(f"ASR fehlgeschlagen: {type(e).__name__}: {e}", model)


def retrieve(query: str, documents: list[str], model_key: str = "embed_baseline", top_k: int = 3) -> dict:
    """Semantische Suche in der Mini-Wissensbasis. Fallback: Wortüberlappung (offline)."""
    model = REGISTRY[model_key]["id"]
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        if not hub_reachable():
            raise RuntimeError("Hub nicht erreichbar")
        m = SentenceTransformer(model)
        import numpy as np  # type: ignore
        q = m.encode([query], normalize_embeddings=True)
        d = m.encode(documents, normalize_embeddings=True)
        sims = (d @ q.T).ravel()
        idx = np.argsort(-sims)[:top_k]
        return {"available": True, "model": model, "hits": [{"doc": documents[i], "score": float(round(sims[i], 3))} for i in idx]}
    except Exception as e:  # noqa: BLE001
        return {**lexical_retrieve(query, documents, top_k), "available": False, "fallback": "lexikalisch", "reason": f"{type(e).__name__}: {e}", "model": model}


def lexical_retrieve(query: str, documents: list[str], top_k: int = 3) -> dict:
    import re
    qw = set(re.findall(r"\w{3,}", query.lower()))
    scored = []
    for d in documents:
        dw = set(re.findall(r"\w{3,}", d.lower()))
        scored.append((len(qw & dw) / (len(qw) or 1), d))
    scored.sort(key=lambda x: -x[0])
    return {"hits": [{"doc": d, "score": round(s, 3)} for s, d in scored[:top_k]], "method": "Wortüberlappung"}
