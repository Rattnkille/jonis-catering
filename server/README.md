# server/ – Anfrage-Pipeline (Formular → Google Sheet)

Diese Dateien liegen **bewusst getrennt von `index.html`**, weil sie auf zwei
externen Systemen laufen, nicht auf der statischen Website:

- `webhook-Code.gs` → läuft im **Google Apps Script** (eurem bestehenden „JONIS Sheets Webhook")
- `anfrage-zu-sheet.php` → kommt in die **`send_email.php` auf dem Hostinger-Server**

Sie sind hier im Repo, damit der Code versioniert und auffindbar ist.

> ⚠️ **Kein echtes Token committen.** In beiden Dateien steht `DEIN_TOKEN_HIER`
> als Platzhalter. Das echte Token nur direkt im Apps Script / auf dem Server
> eintragen – niemals hier ins Repo.

## So wird's scharf geschaltet (einmalig, ~10 Min)

**Teil A – Apps Script (Tabelle empfangsbereit machen)**
1. Apps Script „JONIS Sheets Webhook" öffnen.
2. Inhalt von `webhook-Code.gs` reinkopieren.
3. Oben dein echtes Token bei `SECRET` eintragen (das bisherige übernehmen).
4. **Bereitstellen → Bereitstellung verwalten → Bearbeiten → Neue Version → Speichern.**

**Teil B – send_email.php (Anfrage weiterreichen)**
1. `send_email.php` auf dem Server öffnen (Hostinger Dateimanager).
2. Funktion aus `anfrage-zu-sheet.php` reinkopieren; oben `$webhookUrl` (deine `/exec`-URL)
   und `$secret` eintragen.
3. Den Aufruf `jonis_forward_to_sheet();` direkt **nach dem Mailversand**,
   **vor** der Weiterleitung auf `?success=1` einsetzen.

**Teil C – Test**
1. Auf jonis-catering.de eine Test-Anfrage absenden.
2. In „JONIS Anfragen 2026" sollte sofort eine neue Zeile erscheinen.
3. Erfolg ✅ → Test-Zeile wieder löschen.
