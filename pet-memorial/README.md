# Wieder da — interaktive Erinnerung an dein Haustier

Eine kleine Web-App, mit der du über Mikrofon mit deinem verstorbenen Tier "sprechen" kannst.
Das Tier reagiert mit Aktionen, Lauten und einer kurzen Beschreibung dessen, was es tut.

> Diese App ist als zarte Erinnerung gedacht — nicht als Ersatz. Sei sanft mit dir.

## Was passiert technisch

1. Du hältst das Mikrofon gedrückt und sprichst (deutsch).
2. Der Browser transkribiert dein Sprechen lokal (Web Speech API).
3. Claude bekommt das Transkript + die Persönlichkeit deines Tieres und entscheidet, **wie** es reagiert (Aktion, Sound, kurze Beschreibung).
4. Die App spielt den passenden Video-Clip + Sound ab und blendet die Beschreibung ein.

Alles läuft im Browser. Dein API-Key bleibt nur in deinem LocalStorage.

## Voraussetzungen

- Chrome oder Edge (Web Speech API nötig)
- Ein Claude API-Key: https://console.anthropic.com/settings/keys
- Optional: Video-Clips deines Tieres und Hunde-Sounds (siehe unten)

## Starten

Weil Mikrofon-Zugriff HTTPS oder localhost braucht, kannst du nicht einfach `index.html` doppelklicken. Stattdessen:

```bash
cd pet-memorial
python3 -m http.server 8000
```

Dann im Browser: http://localhost:8000

Beim ersten Start trägst du ein:
- API-Key
- Name des Tieres
- Tierart / Beschreibung
- Persönlichkeit & Erinnerungen (je mehr, desto lebendiger reagiert es)
- Foto (für den Ruhezustand, falls keine Video-Clips da sind)

## Video-Clips generieren

Die App sucht im Ordner `clips/` nach folgenden MP4-Dateien:

| Datei | Aktion |
|---|---|
| `idle.mp4` | Ruhezustand (wird geloopt) |
| `wag.mp4` | Schwanzwedeln |
| `run_to.mp4` | läuft auf die Kamera zu |
| `sit.mp4` | setzt sich hin |
| `lay_down.mp4` | legt sich hin |
| `head_tilt.mp4` | legt den Kopf zur Seite |
| `sleep.mp4` | schläft ruhig |
| `play.mp4` | spielt mit Spielzeug |
| `eat.mp4` | frisst aus dem Napf |
| `look_around.mp4` | schaut sich um |

Fehlt eine Datei, fällt die App auf `idle.mp4` zurück, sonst auf das Foto.

### Mit Runway Gen-3 / Luma Dream Machine / Sora generieren

Lade ein Foto deines Tieres hoch und nutze image-to-video mit z. B. diesen Prompts:

- **idle**: *"The dog stands calmly in soft natural light, breathing gently, blinking, slight head movement. Static camera. 5 seconds."*
- **wag**: *"The dog wags its tail enthusiastically, looking at the camera with bright eyes. Static camera."*
- **run_to**: *"The dog runs joyfully toward the camera through soft grass, ears bouncing."*
- **sit**: *"The dog slowly sits down on its haunches, looking up at the camera attentively."*
- **lay_down**: *"The dog calmly lays down, rests its head on its paws, eyes half-closed."*
- **head_tilt**: *"The dog tilts its head curiously to the side, ears perked."*
- **sleep**: *"Close-up of the dog peacefully sleeping, gentle breathing, eyes closed."*
- **play**: *"The dog playfully jumps and pounces, mouth open in a happy expression."*
- **eat**: *"The dog eats happily from a food bowl, focused and content."*
- **look_around**: *"The dog turns its head, looking around alertly with curious eyes."*

Tipp: kurze Clips (3–5 Sekunden) reichen. Für `idle.mp4` möglichst nahtlos loop-fähig.

## Sounds

Lege MP3-Dateien in `sounds/`:

- `happy_bark.mp3` — fröhliches Bellen
- `soft_woof.mp3` — sanftes leises Woof
- `whine.mp3` — leises Winseln
- `pant.mp3` — Hecheln
- `snore.mp3` — Schnarchen

Royalty-free Sounds findest du auf https://freesound.org (Suche: "dog bark", "dog whine", etc.) oder
https://pixabay.com/sound-effects/search/dog/

Fehlt ein Sound, wird einfach nichts abgespielt — die App läuft trotzdem.

## Persönlichkeit gut beschreiben

Je präziser dein Persönlichkeits-Text, desto eigenständiger reagiert dein Tier. Beispiel:

> Bello war ein 12-jähriger schwarzer Labrador. Sanftmütig, neugierig, hat geliebt zu schwimmen.
> Hat immer den Kopf schief gelegt wenn ich mit ihm gesprochen hab. War etwas tollpatschig,
> hat manchmal das Fressen in der Küche vor dem Napf verteilt. War mein Schatten — überall wo
> ich war, war er auch. Liebster Ort: Sofa, zusammengerollt neben mir. Mochte keine Gewitter.

## Datenschutz

- API-Key und Tier-Daten werden **nur lokal** im Browser gespeichert (LocalStorage).
- Beim Sprechen geht das transkribierte Text an Anthropic (für Claude's Antwort).
- Die Mikrofon-Aufnahme verlässt den Browser nicht — sie wird lokal transkribiert.
- Kein Backend, kein Tracking.

## Bekannte Einschränkungen

- Web Speech API funktioniert in Safari/Firefox nicht zuverlässig — bitte Chrome/Edge nutzen.
- Video-Generierung musst du selbst machen — die App spielt die Clips nur ab.
- Echte Videos deines Tieres sind oft schöner als AI-generierte. Du kannst auch reale Aufnahmen mit denselben Dateinamen verwenden.
