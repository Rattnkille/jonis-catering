"""CLI: python -m forno_twin demo | run <datei> | calibrate | status"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import pipeline, hf_models, learn
from .pipeline import OUT


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "demo"
    if cmd == "demo":
        from .demo_data import load_events
        events = load_events()
        chosen = [e for e in events if e["id"] == (argv[1] if len(argv) > 1 else "SYN-001")][0]
        res = pipeline.run(chosen["text"], event_id=chosen["id"], transcript=chosen.get("transcript"),
                           distance_km=chosen.get("distance_km"), out_dir=OUT / "demo", use_hf="--hf" in argv)
        print(pipeline.summary(res))
        print("Exporte:", *res.get("exports", []), sep="\n  ")
    elif cmd == "run":
        text = Path(argv[1]).read_text(encoding="utf-8")
        res = pipeline.run(text, event_id=Path(argv[1]).stem, synthetic="--real" not in argv, out_dir=OUT / "run")
        print(pipeline.summary(res))
    elif cmd == "calibrate":
        print(json.dumps(learn.calibrate(), ensure_ascii=False, indent=2))
    elif cmd == "status":
        print(json.dumps(hf_models.status(), ensure_ascii=False, indent=2))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
