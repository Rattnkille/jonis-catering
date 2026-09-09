"""Lädt Planungsparameter und überlagert sie mit Kalibrierungen aus dem Lern-Loop."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
PARAMS_PATH = DATA / "parameters.json"
CALIB_PATH = DATA / "calibration.json"


def load_params(with_calibration: bool = True) -> dict:
    with open(PARAMS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    params = {k: dict(v) for k, v in raw.items() if not k.startswith("_")}
    if with_calibration and CALIB_PATH.exists():
        with open(CALIB_PATH, encoding="utf-8") as f:
            calib = json.load(f)
        for k, v in calib.get("overrides", {}).items():
            if k in params:
                params[k] = {**params[k], "value": v["value"], "status": "KALIBRIERT",
                             "note": f"{params[k].get('note', '')} | kalibriert aus {v.get('n_events', '?')} Events am {v.get('updated', '?')}".strip(" |")}
    return params


def p(params: dict, key: str):
    return params[key]["value"]
