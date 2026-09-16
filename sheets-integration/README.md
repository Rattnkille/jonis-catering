# Anfragen-Pipeline: Google Sheet als Anfragen-Datenbank

Ziel: Jede Anfrage aus dem Kontaktformular auf jonis-catering.de landet
zusätzlich zur E-Mail als neue Zeile im Google Sheet **"JONIS Anfragen &
Angebote"**, mit Status "Neu". Von dort übernimmt später die
Angebots-Automatisierung.

Das läuft **nicht** über die Website selbst (kein eigener Server dort möglich),
sondern über ein kleines Google Apps Script, das direkt am Sheet hängt. Das
musst du einmalig selbst einrichten, weil dabei ein Google-Login-Fenster
kommt, das ich nicht für dich klicken kann.

## Schritt für Schritt (ca. 5 Minuten)

1. Öffne das Sheet **"JONIS Anfragen & Angebote"** in Google Drive
   (`sibbingjonathan@gmail.com`).
2. Menü **Erweiterungen → Apps Script**.
3. Der Editor öffnet sich mit einer leeren `Code.gs`. Lösche den Inhalt und
   füge den kompletten Inhalt der Datei [`Code.gs`](./Code.gs) aus diesem
   Ordner ein.
4. Links im Editor auf das Zahnrad-Symbol **Projekteinstellungen** klicken,
   dort unter **Skripteigenschaften** eine neue Eigenschaft anlegen:
   - Name: `WEBHOOK_SECRET`
   - Wert: ein beliebiges, langes Zufallspasswort (z. B. per
     [1Password](https://1password.com/password-generator) generieren) –
     das verhindert, dass Fremde Zeilen in dein Sheet schreiben können.
   - Speichern.
5. Oben rechts auf **Bereitstellen → Neue Bereitstellung**.
   - Typ: **Web App**.
   - Ausführen als: **Ich (deine Google-Adresse)**.
   - Zugriff: **Jeder** (das ist notwendig, damit die Website unangemeldet
     senden kann – der Schutz läuft über das Secret aus Schritt 4, nicht
     über den Google-Zugriff).
   - Auf **Bereitstellen** klicken, Google-Login/Berechtigung bestätigen.
6. Du bekommst eine **Web-App-URL** (endet auf `/exec`). Kopiere sie.
7. Schick mir die Web-App-URL und das Secret aus Schritt 4 (z. B. hier im
   Chat oder – sicherer – direkt in `.mail_config.php` eintragen, siehe
   unten). Ich trage dann Folgendes in `.mail_config.php` auf dem Server ein
   (diese Datei ist nicht im Git-Repo, liegt nur auf Hostinger):

   ```php
   'sheets_webhook_url' => 'https://script.google.com/macros/s/DEINE_ID/exec',
   'sheets_webhook_secret' => 'DEIN_SECRET_AUS_SCHRITT_4',
   ```

   Alternativ kannst du das auch direkt selbst in der `.mail_config.php` auf
   dem Server ergänzen (per Hostinger-Dateimanager oder FTP) – dann muss die
   URL/das Secret nirgends sonst geteilt werden.

## Was danach passiert

- Jede neue Formular-Anfrage schreibt automatisch eine Zeile ins
  Tabellenblatt **"Anfragen"** (wird beim ersten Aufruf automatisch mit
  Kopfzeile angelegt), Status **"Neu"**.
- Die Website-E-Mail an `info@jonis-catering.de` funktioniert davon
  komplett unabhängig weiter – falls die Sheets-Anbindung mal ausfällt oder
  noch nicht eingerichtet ist, passiert einfach nichts Zusätzliches, aber
  nichts bricht.
- Die nächste Ausbaustufe (automatische Angebotserstellung aus diesen
  Zeilen, Freigabe durch dich, Versand) baue ich, sobald das Sheet befüllt
  wird.

## Testen

Nach dem Deployment kannst du testen, indem du das Kontaktformular auf der
Live-Website einmal selbst ausfüllst und prüfst, ob im Sheet eine neue Zeile
mit Status "Neu" erscheint. Falls nicht: prüfe, ob `sheets_webhook_url` und
`sheets_webhook_secret` korrekt in `.mail_config.php` stehen.
