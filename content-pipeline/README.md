# JONIS Content-Pipeline

Rohmaterial rein, fertige TikToks raus. Wird **nicht** auf die Website
hochgeladen (siehe `exclude` in `.github/workflows/deploy.yml`).

## So läuft es

1. **Joni** lädt Videos und Fotos in den Drive-Ordner **JONIS Inbox**.
2. **Jeden Freitag** startet eine geplante Claude-Aufgabe in der Cloud und
   arbeitet `WEEKLY.md` ab: Material sichten, 7 Schnittpläne schreiben,
   mit HyperFrames rendern, prüfen, Captions schreiben, alles in Drive ablegen.
3. **Joni** bekommt eine Nachricht, schaut die Vorschau an und gibt frei.
4. **Claude in Chrome** führt den Upload-Auftrag in TikTok Studio aus
   (Zeitplan Mo bis So, 18:00 Uhr).

## Dateien

| Datei | Zweck |
|---|---|
| `WEEKLY.md` | Arbeitsanweisung für den Wochenlauf |
| `config.json` | Drive-Ordner-IDs, Videos pro Woche, Größengrenze Web-Version |
| `drive.py` | Drive lesen und schreiben (über das Apps-Script-Token) |
| `sheets.py` | Kontaktbögen und `index.json` zum Sichten |
| `render.py` | Schnittplan zu MP4 (Vollversion, `_web.mp4`, Kontrollbogen) |
| `template/` | HyperFrames-Vorlage im Playbook-Stil |
| `apps-script/token.gs` | Einmal in Jonis Google-Konto einrichten |

## Einrichtung (einmalig)

1. `apps-script/token.gs` wie im Kopf der Datei beschrieben als Web-App bereitstellen.
2. In der Cloud-Umgebung zwei Umgebungsvariablen anlegen:
   `JONIS_DRIVE_TOKEN_URL` (Web-App-URL) und `JONIS_DRIVE_KEY` (der KEY aus dem Skript).
3. Test: `python3 drive.py whoami` zeigt Jonis E-Mail-Adresse.

Ohne diese Variablen kann die Pipeline nur per Link freigegebene Ordner lesen
und nichts zurückschreiben.

## Schnittplan

```json
{
  "id": "JONIS_TikTok_18_Hinter_den_Kulissen",
  "segments": [
    {"src": "IMG_2439.MOV", "start": 0.0, "dur": 2.2, "focus_x": 0.62,
     "text": ["So kommt sie aus", "dem Steinofen"], "accent_first": false},
    {"src": "IMG_0081.HEIC", "dur": 2.0, "zoom": 1.08, "text": ["Von Hand belegt"]}
  ],
  "end": {"src": "f99862c7.jpg", "focus_x": 0.7, "lines": ["Pizza aus dem Steinofen", "für deine Feier"], "dur": 2.6}
}
```

- `src`: Dateiname in `work/media/` (Video oder Foto, auch HEIC).
- `start`, `dur`: Ausschnitt in Sekunden. `speed` optional (z. B. 1.5).
- `focus_x`: 0 = linker Bildrand, 1 = rechter Rand beim 9:16-Zuschnitt.
- `text`: 0 bis 2 Zeilen, dunkle Box, weiße Schrift, oberes Drittel.
  `accent_first: true` färbt die erste Zeile Amber.
- `zoom`: langsamer Zoom bei Fotos (Standard 1.08).
- `end`: Endkarte mit JONIS, Pizza Catering, zwei Zeilen, jonis-catering.de.

## Lokal testen

```bash
pip install -r requirements.txt
python3 sheets.py work/media work/sheets
python3 render.py plans/<plan>.json
```

Rendern braucht Node 18+, ffmpeg und lädt HyperFrames 0.8.174 per `npx`.
