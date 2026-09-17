# Ist-Daten nach dem Event (Waste Lens)

Pro Event eine JSON-Datei, ohne personenbezogene Daten. Nur `synthetic: false` kalibriert Parameter.

```json
{
  "event_id": "EVT-2026-09-20",
  "synthetic": false,
  "guests_actual": 84,
  "pizzas_produced": 190,
  "leftover_pizzas": 9,
  "leftover_dough_kg": 2.5,
  "leftover_by_sort": [{"name": "La Diavola", "leftover": 4}],
  "helpers_actual": 3,
  "hours_per_helper_actual": 8.5,
  "serving_minutes_actual": 165,
  "weather": "trocken",
  "notes": "Zufahrt eng, 15 min Verzögerung"
}
```

Auswertung: `python -m forno_twin calibrate` (schreibt `data/calibration.json`, gedämpft per EMA).
Die Ist-JSON-Dateien werden nicht committet (`.gitignore`), damit keine Betriebsdaten versehentlich öffentlich werden.
