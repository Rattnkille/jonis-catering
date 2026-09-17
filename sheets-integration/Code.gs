/**
 * JONIS Anfragen-Pipeline – Google Apps Script Web App.
 *
 * Nimmt neue Kontaktformular-Anfragen von jonis-catering.de per POST entgegen
 * und schreibt sie als neue Zeile in das Tabellenblatt "Anfragen" der
 * verknüpften Google-Sheets-Datei "JONIS Anfragen & Angebote".
 *
 * Deployment: siehe README.md in diesem Ordner. Dieses Script läuft NICHT
 * auf der Website – es wird manuell in script.google.com eingefügt und dort
 * als Web App bereitgestellt.
 */

var SHEET_NAME = 'Anfragen';

var HEADER_ROW = [
  'Zeitstempel',
  'Status',
  'Name',
  'E-Mail',
  'Telefon',
  'Anlass',
  'Wunschdatum',
  'Anzahl Gäste',
  'Veranstaltungsort',
  'Zeitfenster',
  'Budget (ca.)',
  'Ernährung / Allergien',
  'Nachricht',
];

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);

    var expectedSecret = PropertiesService.getScriptProperties().getProperty('WEBHOOK_SECRET');
    if (expectedSecret && body.secret !== expectedSecret) {
      return jsonResponse({ ok: false, error: 'unauthorized' });
    }

    var sheet = ensureSheet();
    sheet.appendRow([
      new Date(),
      'Neu',
      body.name || '',
      body.email || '',
      body.phone || '',
      body.occasion || '',
      body.date || '',
      body.guests || '',
      body.location || '',
      body.timeframe || '',
      body.budget || '',
      body.dietary || '',
      body.message || '',
    ]);

    return jsonResponse({ ok: true });
  } catch (error) {
    return jsonResponse({ ok: false, error: String(error) });
  }
}

function ensureSheet() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = spreadsheet.insertSheet(SHEET_NAME);
  }

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADER_ROW);
    sheet.getRange(1, 1, 1, HEADER_ROW.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }

  return sheet;
}

function jsonResponse(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
