<?php
/**
 * Kontaktformular-Handler für Jonis Catering.
 * Nimmt die POST-Daten aus dem Anfrageformular (index.html) entgegen,
 * versendet sie per E-Mail und leitet mit Status-Parametern zurück,
 * die das Inline-JS in index.html auswertet (?success=1 / ?error=...).
 */

$redirect = 'index.html';

// Nur POST-Anfragen verarbeiten.
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: ' . $redirect);
    exit;
}

// Header-Injection verhindern: Zeilenumbrüche aus einzeiligen Feldern entfernen.
function clean_field($value) {
    return trim(str_replace(["\r", "\n", "%0a", "%0d", "%0A", "%0D"], '', (string) $value));
}

$name     = clean_field($_POST['name']     ?? '');
$email    = clean_field($_POST['email']    ?? '');
$phone    = clean_field($_POST['phone']    ?? '');
$occasion = clean_field($_POST['occasion'] ?? '');
$date     = clean_field($_POST['date']     ?? '');
$guests   = clean_field($_POST['guests']   ?? '');
$message  = trim($_POST['message'] ?? '');

// Pflichtfelder prüfen (Name + E-Mail, wie im Formular markiert).
if ($name === '' || $email === '') {
    header('Location: ' . $redirect . '?error=required#kontakt');
    exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header('Location: ' . $redirect . '?error=email#kontakt');
    exit;
}

$to      = 'info@jonis-catering.de';
$subject = 'Neue Catering-Anfrage von ' . $name;

$body  = "Neue Anfrage über das Kontaktformular auf jonis-catering.de:\n\n";
$body .= 'Name:         ' . $name . "\n";
$body .= 'E-Mail:       ' . $email . "\n";
$body .= 'Telefon:      ' . ($phone    !== '' ? $phone    : '-') . "\n";
$body .= 'Anlass:       ' . ($occasion !== '' ? $occasion : '-') . "\n";
$body .= 'Wunschdatum:  ' . ($date     !== '' ? $date     : '-') . "\n";
$body .= 'Anzahl Gäste: ' . ($guests   !== '' ? $guests   : '-') . "\n\n";
$body .= "Nachricht:\n" . ($message !== '' ? $message : '-') . "\n";

// Absender auf eigener Domain (SPF/DMARC-konform), Antwort an Anfragenden.
$headers  = 'From: Jonis Catering Website <info@jonis-catering.de>' . "\r\n";
$headers .= 'Reply-To: ' . $email . "\r\n";
$headers .= 'Content-Type: text/plain; charset=UTF-8' . "\r\n";

// Betreff UTF-8-kodieren (Umlaute korrekt darstellen).
$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';

if (@mail($to, $encodedSubject, $body, $headers)) {
    header('Location: ' . $redirect . '?success=1#kontakt');
} else {
    header('Location: ' . $redirect . '?error=send#kontakt');
}
exit;
