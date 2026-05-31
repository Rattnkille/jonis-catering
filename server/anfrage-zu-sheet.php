<?php
/**
 * JONIS – Anfrage zusätzlich ins Google Sheet schreiben
 * =====================================================
 * Diesen Code-Block in die BESTEHENDE send_email.php einfügen –
 * direkt NACHDEM die E-Mail verschickt wurde und BEVOR auf
 * "?success=1" weitergeleitet wird.
 *
 * Dein funktionierender Mail-Versand wird NICHT angefasst.
 *
 * Vorher zwei Werte eintragen:
 *   1. $webhookUrl  = deine Apps-Script Web-App-URL (endet auf /exec)
 *   2. $secret      = dasselbe Token wie im Apps Script (SECRET)
 */

function jonis_forward_to_sheet() {
    $webhookUrl = 'https://script.google.com/macros/s/XXXXXXXXXXXX/exec'; // ← deine /exec-URL
    $secret     = 'DEIN_TOKEN_HIER';                                       // ← dasselbe Token wie im Apps Script

    $payload = json_encode([
        'secret' => $secret,
        'action' => 'append_anfrage',
        'data'   => [
            'name'      => $_POST['name']     ?? '',
            'email'     => $_POST['email']    ?? '',
            'telefon'   => $_POST['phone']    ?? '',
            'datum'     => $_POST['date']     ?? '',
            'personen'  => $_POST['guests']   ?? '',
            'anlass'    => $_POST['occasion'] ?? '',
            'nachricht' => $_POST['message']  ?? '',
            // 'uhrzeit', 'ort', 'paket' gibt's im Formular (noch) nicht → bleiben leer
        ],
    ]);

    $ch = curl_init($webhookUrl);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $payload,
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 8,            // blockiert den Nutzer nicht
        CURLOPT_FOLLOWLOCATION => true,         // Apps Script leitet auf googleusercontent um
    ]);
    curl_exec($ch);
    curl_close($ch);
    // Bewusst "fire and forget": Wenn das Sheet mal nicht antwortet,
    // ist die E-Mail trotzdem raus und der Nutzer sieht die Erfolgsseite.
}

// ▸ Diese eine Zeile an der richtigen Stelle in send_email.php aufrufen:
jonis_forward_to_sheet();
