<?php
/**
 * Wartelisten-Handler für die PizzaPool-Landingpage (plattform/index.html).
 * Nimmt die POST-Daten des Wartelisten-Formulars entgegen, versendet sie
 * per E-Mail und leitet mit Status-Parametern zurück, die das Inline-JS
 * in index.html auswertet (?success=1 / ?error=...).
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

$name      = clean_field($_POST['name']      ?? '');
$email     = clean_field($_POST['email']     ?? '');
$ort       = clean_field($_POST['ort']       ?? '');
$instagram = clean_field($_POST['instagram'] ?? '');
$setup     = clean_field($_POST['setup']     ?? '');

if ($name === '' || $email === '' || $ort === '') {
    header('Location: ' . $redirect . '?error=required#warteliste');
    exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header('Location: ' . $redirect . '?error=email#warteliste');
    exit;
}

$to      = 'info@jonis-catering.de';
$subject = 'PizzaPool-Warteliste: ' . $name . ' (' . $ort . ')';

$body  = "Neuer Eintrag auf der PizzaPool-Warteliste:\n\n";
$body .= 'Name/Betrieb: ' . $name . "\n";
$body .= 'E-Mail:       ' . $email . "\n";
$body .= 'Stadt/Region: ' . $ort . "\n";
$body .= 'Instagram:    ' . ($instagram !== '' ? $instagram : '-') . "\n";
$body .= 'Setup:        ' . ($setup     !== '' ? $setup     : '-') . "\n";

// Absender auf eigener Domain (SPF/DMARC-konform), Antwort an Interessent:in.
$headers  = 'From: PizzaPool Warteliste <info@jonis-catering.de>' . "\r\n";
$headers .= 'Reply-To: ' . $email . "\r\n";
$headers .= 'Content-Type: text/plain; charset=UTF-8' . "\r\n";

// Betreff UTF-8-kodieren (Umlaute korrekt darstellen).
$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';

if (@mail($to, $encodedSubject, $body, $headers)) {
    header('Location: ' . $redirect . '?success=1#warteliste');
} else {
    header('Location: ' . $redirect . '?error=send#warteliste');
}
exit;
