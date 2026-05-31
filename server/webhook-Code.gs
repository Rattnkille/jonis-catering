/**
 * JONIS Sheets Webhook – Code.gs
 * =================================
 * Dies ist die ERWEITERTE Version eures bestehenden Webhooks.
 * NEU: action "append_anfrage" schreibt Web-Formular-Anfragen in die
 *      Tabelle "JONIS Anfragen 2026".
 *
 * ▸ Token unten (SECRET) durch DEIN echtes Token ersetzen
 *   (steht in deinem bisherigen Script – einfach übernehmen).
 * ▸ Danach: Bereitstellen → Bereitstellung verwalten → neue Version.
 */

const SHEET_ID          = "1lkUY1DZOf8H6Qs-oPOq8b6F_Aw911BWk_Oy5Zi88334"; // Einsatzplanung 2026
const ANFRAGEN_SHEET_ID = "1j5Cnv97cBmrebW9e2R6sCrltndHGNBpGAnqQwHCKXmw"; // Anfragen 2026
const SECRET            = "DEIN_TOKEN_HIER"; // ← dein bestehendes Token eintragen, NICHT committen

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    if (body.secret !== SECRET) return j({ ok: false, error: "unauthorized" });

    const ss = SpreadsheetApp.openById(SHEET_ID);
    const action = body.action;
    const d = body.data || {};

    if (action === "ping") {
      return j({ ok: true, sheet: ss.getName() });
    }

    if (action === "append_stunden") {
      const s = ss.getSheetByName("Stundenerfassung");
      if (!s) return j({ ok: false, error: "Tab 'Stundenerfassung' nicht gefunden" });
      s.appendRow([d.datum, d.mitarbeiter, d.event, d.beginn, d.ende, d.stunden, d.bemerkungen || ""]);
      return j({ ok: true, message: "Stunden eingetragen" });
    }

    if (action === "append_einsatz") {
      const s = ss.getSheetByName("Einsatz-Planung");
      if (!s) return j({ ok: false, error: "Tab 'Einsatz-Planung' nicht gefunden" });
      s.appendRow([d.datum, d.event, d.uhrzeit, d.ort, d.slot1 || "", d.slot2 || "", d.slot3 || "", d.persGeplant || "", d.status || ""]);
      return j({ ok: true, message: "Buchung eingetragen" });
    }

    if (action === "update_status") {
      const s = ss.getSheetByName("Einsatz-Planung");
      const data = s.getDataRange().getValues();
      for (let i = 0; i < data.length; i++) {
        if (data[i][1] && data[i][1].toString().toLowerCase().includes((d.eventMatch || "").toLowerCase())) {
          s.getRange(i + 1, 9).setValue(d.status);
          return j({ ok: true, message: "Status aktualisiert: Zeile " + (i + 1) });
        }
      }
      return j({ ok: false, error: "Event nicht gefunden" });
    }

    // ── NEU: Web-Anfrage in "JONIS Anfragen 2026" eintragen ──
    if (action === "append_anfrage") {
      const aSS = SpreadsheetApp.openById(ANFRAGEN_SHEET_ID);
      const s = aSS.getSheets()[0]; // erstes Tab ("JONIS Anfragen 2026")
      const eingang = Utilities.formatDate(new Date(), "Europe/Berlin", "dd.MM.yyyy HH:mm");
      // Spalten: Eingang | Name | E-Mail | Telefon | Eventdatum | Uhrzeit |
      //          Personen | Ort / PLZ | Anlass | Paket-Wunsch | Nachricht |
      //          Status | Angebot raus | Notiz
      s.appendRow([
        eingang,
        d.name      || "",
        d.email     || "",
        d.telefon   || "",
        d.datum     || "",
        d.uhrzeit   || "",
        d.personen  || "",
        d.ort       || "",
        d.anlass    || "",
        d.paket     || "",
        d.nachricht || "",
        "Neu",   // Status
        "",      // Angebot raus
        ""       // Notiz
      ]);
      return j({ ok: true, message: "Anfrage eingetragen" });
    }

    return j({ ok: false, error: "unbekannte action: " + action });
  } catch (err) {
    return j({ ok: false, error: err.message });
  }
}

function doGet() {
  return j({ ok: true, message: "JONIS Webhook läuft" });
}

function j(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
