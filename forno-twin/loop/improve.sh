#!/usr/bin/env bash
# FORNO TWIN – deterministischer Verbesserungs-Loop (kostenlos, ohne Modelle, ohne Credits).
# 1) Tests  2) Evaluation (Metriken + Verlauf)  3) Kalibrierung aus Ist-Daten  4) Statusbericht
# Exit-Code != 0, wenn Tests fehlschlagen oder ein kritischer Allergenfehler auftritt.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python3}"
echo "== FORNO TWIN Loop $(date -u +%FT%TZ) =="
echo "-- Tests"
$PY -m pytest tests -q 2>/dev/null || $PY -m unittest discover -s tests -q
echo "-- Evaluation"
$PY eval/run_eval.py > /tmp/forno_eval.json
cat /tmp/forno_eval.json
echo "-- Kalibrierung"
$PY -m forno_twin calibrate > /tmp/forno_calib.json
cat /tmp/forno_calib.json
echo "-- Loop-Bericht"
$PY loop/report.py
echo "== fertig =="
