"""Schreibt docs/loop-status.md: Verlauf der Evaluationen, Kalibrierungsstand, offene Verbesserungen.

Der Bericht ist die Übergabe an den nächsten Loop-Lauf (Mensch oder KI-Session).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
HIST = ROOT / "eval" / "history.jsonl"
CALIB = ROOT / "data" / "calibration.json"
OUT = ROOT / "docs" / "loop-status.md"
BACKLOG = ROOT / "loop" / "backlog.json"


def main():
    runs = [json.loads(l) for l in HIST.read_text(encoding="utf-8").splitlines() if l.strip()] if HIST.exists() else []
    calib = json.loads(CALIB.read_text(encoding="utf-8")) if CALIB.exists() else {}
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8")) if BACKLOG.exists() else {"items": []}
    last = runs[-1] if runs else {}
    trend = ""
    if len(runs) >= 2:
        d = last["accuracy"] - runs[-2]["accuracy"]
        trend = f" (Δ {d:+.1%} zum Vorlauf)"
    lines = ["# FORNO TWIN – Loop-Status", "", f"Letzter Lauf: {last.get('ts', '–')}", "",
             "## Kennzahlen des letzten Laufs", "",
             f"- Genauigkeit Einzelprüfungen: **{last.get('accuracy', 0):.1%}**{trend}",
             f"- Testfälle vollständig bestanden: **{last.get('cases_ok', 0)}/{last.get('cases', 0)}**",
             f"- Kritische Allergenfehler: **{last.get('allergen_critical_errors', '–')}** (muss 0 sein)",
             f"- Ø Vollständigkeit Eventakte: {last.get('avg_completeness', 0):.0%}",
             f"- Fehlgeschlagen: {', '.join(last.get('failed', [])) or 'keine'}", "",
             "## Verlauf (letzte 10 Läufe)", "", "| Zeit | Genauigkeit | Fälle ok | Allergenfehler |", "|---|---|---|---|"]
    for r in runs[-10:]:
        lines.append(f"| {r['ts']} | {r['accuracy']:.1%} | {r['cases_ok']}/{r['cases']} | {r['allergen_critical_errors']} |")
    lines += ["", "## Kalibrierung aus Ist-Daten", "",
              f"- Reale Events mit Ist-Daten: **{calib.get('n_real_events', 0)}**",
              "- Überschriebene Parameter: " + (", ".join(f"{k}={v['value']}" for k, v in calib.get("overrides", {}).items()) or "keine (Parameter bleiben ANNAHME)"),
              *[f"- {n}" for n in calib.get("notes", [])], "",
              "## Verbesserungs-Backlog (priorisiert)", ""]
    for i, it in enumerate(sorted(backlog["items"], key=lambda x: x.get("priority", 9)), 1):
        lines.append(f"{i}. [{it.get('status', 'offen')}] **{it['title']}** – {it.get('why', '')} (Messgröße: {it.get('metric', '–')})")
    lines += ["", "## Regeln für den nächsten Loop-Lauf", "",
              "1. Erst `bash loop/improve.sh`. Rote Tests oder Allergenfehler > 0 haben Vorrang vor allem anderen.",
              "2. Genau einen Backlog-Punkt umsetzen, mit neuem Testfall in `data/synthetic_events.json` und Prüfung in `eval/run_eval.py`.",
              "3. Genauigkeit darf nicht sinken. Sinkt sie, Änderung zurücknehmen.",
              "4. Keine Preise, Kosten, Allergene oder Kapazitäten erfinden. Neue Parameter bekommen Status ANNAHME oder TBD.",
              "5. Backlog in `loop/backlog.json` pflegen (erledigt markieren, neue Lücken aus Fehlerbeispielen ergänzen).",
              "6. Änderungen als PR auf Branch `claude/forno-twin-loop` mit dem Loop-Bericht im PR-Text. Nichts veröffentlichen, keine Kundenkontakte, keine Bezahlkosten.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"geschrieben: {OUT}")


if __name__ == "__main__":
    main()
