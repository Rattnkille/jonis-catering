# Wochenlauf: 7 TikToks aus der JONIS Inbox

Diese Datei ist die Arbeitsanweisung für die geplante Aufgabe (jeden Freitag).
Ziel: Joni lädt nur Rohmaterial in **JONIS Inbox**. Alles bis zur Freigabe
passiert hier automatisch. Veröffentlicht wird **nie** ohne Jonis Freigabe.

Alle Befehle laufen in `content-pipeline/`. Ordner-IDs stehen in `config.json`.

## 0. Vorbereitung

```bash
pip install -q -r requirements.txt
python3 drive.py whoami      # muss eine E-Mail-Adresse zeigen
```

- Zeigt `whoami` keinen Zugang: Abbrechen. Joni in einer kurzen Nachricht
  sagen, dass `JONIS_DRIVE_TOKEN_URL` / `JONIS_DRIVE_KEY` in der
  Cloud-Umgebung fehlen oder das Apps-Script nicht antwortet (README, Einrichtung).
- `PLAYBOOK.md` aus Drive laden und vollständig lesen. Es gilt immer die
  Drive-Version: `python3 drive.py get <playbook-id> work/PLAYBOOK.md`.
- `posting_log.csv` laden: `python3 drive.py get <posting_log-id> work/posting_log.csv`.
- Den letzten geplanten Termin im Log finden. Die neue Woche beginnt am Tag danach
  (Mo bis So, je 18:00 Uhr). Die Videonummer zählt vom letzten Eintrag weiter
  (`JONIS_TikTok_18_...`).

## 1. Material holen

```bash
python3 drive.py ls <inbox-id> > work/inbox.json
python3 drive.py get <datei-id> work/media/<name>   # für jede Datei, Unterordner auslassen
python3 sheets.py work/media work/sheets
```

- Jeden Kontaktbogen in `work/sheets/` ansehen. Notieren: was zu sehen ist,
  gute Sekunden, Hook-Momente (Ergebnis oder Spannung in 1,5 Sek.), Wackler.
- Erkennbare Kinder: Clip nicht verwenden. Erkennbare Gäste: verwenden ist
  okay, aber in der Freigabe-Nachricht pro Video nennen.
- Reicht das neue Material nicht für 7 gute Videos, unbenutzte Fotos aus
  `fotos_export` dazunehmen (alles, was nicht in der Spalte `clips` des Logs steht).
  Reicht es dann immer noch nicht: lieber weniger Videos bauen als schwache.
  Nie ein bereits gepostetes Video wiederholen.

## 2. Schnittpläne schreiben

Pro Video eine Datei `plans/<id>.json` (Format: README, Abschnitt Schnittplan).

- Formate rotieren, mindestens 2 Videos mit Hook 2, 3 oder 4 aus der
  Hook-Bibliothek im Playbook. Serien (Umbau Teil N) fortsetzen, wenn Material passt.
- 12 bis 20 Sekunden, Szenen 1,8 bis 2,6 Sek., erste Szene = stärkster Moment.
- Texte: Du-Form, immer "Steinofen", keine Emojis, keine Gedankenstriche,
  max. 2 Zeilen mit je höchstens ca. 26 Zeichen. Nur belegte Fakten (keine
  erfundenen Zahlen, Preise, Rekorde, Kundenstimmen).
- `focus_x` so wählen, dass das Motiv im 9:16-Ausschnitt bleibt (Bogen prüfen).
- Endkarte mit 2 Zeilen passend zum Anlass.

## 3. Rendern und prüfen

```bash
python3 render.py plans/<id>.json
```

- Pro Video `work/out/check_<id>.jpg` ansehen: Motiv im Bild, Text lesbar,
  nichts abgeschnitten, kein schwarzes Bild. Bei Fehlern Plan anpassen und neu rendern.
- `render.py` bricht ab, wenn `hyperframes check` scheitert. Ursache beheben,
  nicht umgehen.

## 4. Captions

`work/out/Captions_Woche_<TT>-<TT.MM>.txt` im Stil der bisherigen Dateien:
Kopfzeile mit Woche, dann pro Tag `MO 26.10. | <id>`, Caption nach der
Formel im Playbook (Frage oder Story, was man sieht, sanfter CTA), 6 bis 10 Hashtags.

## 5. Ablegen in Drive

```bash
python3 drive.py put work/out/<id>.mp4 <fertig-id>
python3 drive.py put work/out/<id>_web.mp4 <fertig-id>
python3 drive.py put work/out/check_<id>.jpg <arbeitsordner-id>
python3 drive.py put work/out/<id>.mp4 <fertig_zum_posten-id>
python3 drive.py put work/out/Captions_Woche_....txt <fertig_zum_posten-id>
```

- Pläne sichern: Ordner `plans` im Arbeitsordner (`drive.py mkdir plans <arbeitsordner-id>`),
  dort alle `plans/*.json` ablegen.
- `posting_log.csv` um je eine Zeile ergänzen (`datum,video,clips,hook,status`,
  Status `gebaut wartet auf Freigabe`) und mit `drive.py update` zurückschreiben.
- Benutzte Inbox-Dateien nach `JONIS Inbox/verarbeitet` verschieben
  (`drive.py mkdir verarbeitet <inbox-id>`, dann `drive.py mv`). Unbenutzte bleiben liegen.

## 6. Upload-Auftrag

`work/out/UPLOAD_AUFTRAG_<datum>.md` nach `fertig_zum_posten` legen. Inhalt:
pro Tag Datum, Uhrzeit 18:00, Dateiname der `_web.mp4` in `fertig`, Caption.
Dazu die Einstellungen aus dem Playbook (Standort Bremen, Kommentare und
Wiederverwendung an, Beitragsinhalt "Deine Marke", KI-generiert aus, Sound im
TikTok-Editor wählen). Diese Datei arbeitet Claude in Chrome nach der Freigabe ab.

## 7. Nachricht an Joni (Ende des Laufs)

Kurz, scannbar, auf Deutsch:
- Wie viele Videos gebaut, für welche Tage, je Hook in einer Zeile.
- Was Joni entscheiden muss: erkennbare Gäste, unsichere Aussagen, zu wenig Material.
- Freigabe so erfragen: "Antworte mit `Freigabe alle` oder z. B. `Freigabe 1-5, 6 Text ändern`".
- Danach: "Sag Claude in Chrome: Upload-Auftrag <datum> ausführen."

Antwortet Joni in dieser Sitzung mit Änderungswünschen: Plan anpassen, neu
rendern, Dateien in Drive ersetzen (`drive.py update`), Log anpassen.
Nach `Freigabe`: Status im Log auf `freigegeben` setzen.
