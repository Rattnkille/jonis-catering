/**
 * JONIS Content-Pipeline: gibt der Cloud-Pipeline ein kurzlebiges Drive-Token.
 *
 * Einrichtung (einmalig, ca. 5 Minuten):
 * 1. script.google.com > Neues Projekt > diesen Code einfügen.
 * 2. Projekteinstellungen > Skripteigenschaften > Eigenschaft "KEY" mit einem
 *    langen Zufallswert anlegen (z. B. 40 Zeichen aus einem Passwortmanager).
 * 3. Bereitstellen > Neue Bereitstellung > Typ "Web-App",
 *    Ausführen als: "Ich", Zugriff: "Jeder". Zugriff erlauben.
 * 4. Die Web-App-URL und den KEY in der Cloud-Umgebung als
 *    JONIS_DRIVE_TOKEN_URL und JONIS_DRIVE_KEY hinterlegen.
 *
 * Das Token gilt ca. 1 Stunde. Ohne richtigen KEY gibt das Skript nichts heraus.
 */
function doGet(e) {
  var key = PropertiesService.getScriptProperties().getProperty('KEY');
  if (!key || !e || !e.parameter || e.parameter.key !== key) {
    return json_({ error: 'forbidden' });
  }
  return json_({ token: ScriptApp.getOAuthToken() });
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Wird nie aufgerufen. Sorgt nur dafür, dass Google den vollen Drive-Zugriff abfragt.
function scopeAnchor_() {
  DriveApp.getRootFolder();
}
