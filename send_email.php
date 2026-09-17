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

function encoded_header($value) {
    return '=?UTF-8?B?' . base64_encode($value) . '?=';
}

function smtp_read_response($socket, $expectedCode) {
    $response = '';
    while (($line = fgets($socket, 515)) !== false) {
        $response .= $line;
        if (strlen($line) >= 4 && $line[3] === ' ') {
            break;
        }
    }

    $code = (int) substr($response, 0, 3);
    if ($code !== $expectedCode) {
        throw new RuntimeException('SMTP expected ' . $expectedCode . ', got ' . trim($response));
    }

    return $response;
}

function smtp_command($socket, $command, $expectedCode) {
    fwrite($socket, $command . "\r\n");
    return smtp_read_response($socket, $expectedCode);
}

function dot_stuff($message) {
    $message = str_replace(["\r\n", "\r"], "\n", $message);
    $message = str_replace("\n.", "\n..", $message);
    return str_replace("\n", "\r\n", $message);
}

function load_smtp_config() {
    $config = [];
    $configFile = __DIR__ . '/.mail_config.php';

    if (is_readable($configFile)) {
        $loadedConfig = require $configFile;
        if (is_array($loadedConfig)) {
            $config = $loadedConfig;
        }
    }

    return array_merge([
        'host' => getenv('SMTP_HOST') ?: '',
        'port' => getenv('SMTP_PORT') ?: 465,
        'encryption' => getenv('SMTP_ENCRYPTION') ?: 'ssl',
        'username' => getenv('SMTP_USERNAME') ?: '',
        'password' => getenv('SMTP_PASSWORD') ?: '',
        'from_email' => getenv('SMTP_FROM_EMAIL') ?: 'info@jonis-catering.de',
        'from_name' => getenv('SMTP_FROM_NAME') ?: 'Jonis Catering Website',
    ], array_filter($config, static function ($value) {
        return $value !== null && $value !== '';
    }));
}

function send_via_smtp($to, $subject, $body, $replyTo, $config) {
    $host = (string) $config['host'];
    $port = (int) $config['port'];
    $encryption = strtolower((string) $config['encryption']);
    $username = (string) $config['username'];
    $password = (string) $config['password'];
    $fromEmail = (string) $config['from_email'];
    $fromName = (string) $config['from_name'];

    if ($host === '' || $username === '' || $password === '') {
        return false;
    }

    $transport = $encryption === 'ssl' ? 'ssl://' : '';
    $socket = @stream_socket_client($transport . $host . ':' . $port, $errno, $errstr, 20);
    if (!$socket) {
        throw new RuntimeException('SMTP connection failed: ' . $errstr . ' (' . $errno . ')');
    }

    stream_set_timeout($socket, 20);

    try {
        smtp_read_response($socket, 220);
        smtp_command($socket, 'EHLO jonis-catering.de', 250);

        if ($encryption === 'tls') {
            smtp_command($socket, 'STARTTLS', 220);
            if (!@stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) {
                throw new RuntimeException('SMTP STARTTLS failed');
            }
            smtp_command($socket, 'EHLO jonis-catering.de', 250);
        }

        smtp_command($socket, 'AUTH LOGIN', 334);
        smtp_command($socket, base64_encode($username), 334);
        smtp_command($socket, base64_encode($password), 235);

        smtp_command($socket, 'MAIL FROM:<' . $fromEmail . '>', 250);
        smtp_command($socket, 'RCPT TO:<' . $to . '>', 250);
        smtp_command($socket, 'DATA', 354);

        $headers = [
            'Date: ' . date(DATE_RFC2822),
            'From: ' . encoded_header($fromName) . ' <' . $fromEmail . '>',
            'Reply-To: ' . $replyTo,
            'To: ' . $to,
            'Subject: ' . encoded_header($subject),
            'MIME-Version: 1.0',
            'Content-Type: text/plain; charset=UTF-8',
            'Content-Transfer-Encoding: 8bit',
        ];

        fwrite($socket, dot_stuff(implode("\r\n", $headers) . "\r\n\r\n" . $body) . "\r\n.\r\n");
        smtp_read_response($socket, 250);
        smtp_command($socket, 'QUIT', 221);
        fclose($socket);

        return true;
    } catch (Throwable $exception) {
        fclose($socket);
        throw $exception;
    }
}

function has_smtp_config($config) {
    return (string) $config['host'] !== ''
        && (string) $config['username'] !== ''
        && (string) $config['password'] !== '';
}

function load_sheets_webhook_config() {
    $config = [];
    $configFile = __DIR__ . '/.mail_config.php';

    if (is_readable($configFile)) {
        $loadedConfig = require $configFile;
        if (is_array($loadedConfig)) {
            $config = $loadedConfig;
        }
    }

    return array_merge([
        'url' => getenv('SHEETS_WEBHOOK_URL') ?: '',
        'secret' => getenv('SHEETS_WEBHOOK_SECRET') ?: '',
    ], array_filter([
        'url' => $config['sheets_webhook_url'] ?? null,
        'secret' => $config['sheets_webhook_secret'] ?? null,
    ], static function ($value) {
        return $value !== null && $value !== '';
    }));
}

// Meldet eine neue Anfrage an die Google-Sheets-Pipeline (Anfragen & Angebote).
// Rein informativ: schlägt das fehl, darf das die Bestätigungsmail an den Kunden
// nicht verhindern, daher niemals eine Exception nach außen durchreichen.
function notify_sheets_webhook($data, $config) {
    $url = (string) $config['url'];
    if ($url === '' || !function_exists('curl_init')) {
        return;
    }

    $payload = json_encode(array_merge($data, ['secret' => (string) $config['secret']]));

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_TIMEOUT => 5,
    ]);
    curl_exec($ch);
    if (curl_errno($ch)) {
        error_log('Kontaktformular Sheets-Webhook-Fehler: ' . curl_error($ch));
    }
    curl_close($ch);
}

function redirect_success($redirect) {
    header('Location: ' . $redirect . '?success=1#kontakt');
    exit;
}

$name      = clean_field($_POST['name']      ?? '');
$email     = clean_field($_POST['email']     ?? '');
$phone     = clean_field($_POST['phone']     ?? '');
$occasion  = clean_field($_POST['occasion']  ?? '');
$date      = clean_field($_POST['date']      ?? '');
$guests    = clean_field($_POST['guests']    ?? '');
$location  = clean_field($_POST['location']  ?? '');
$timeframe = clean_field($_POST['timeframe'] ?? '');
$budget    = clean_field($_POST['budget']    ?? '');
$dietary   = clean_field($_POST['dietary']   ?? '');
$website   = clean_field($_POST['website']   ?? '');
$started   = (int) ($_POST['form_started_at'] ?? 0);
$message   = trim($_POST['message'] ?? '');

// Einfacher Bot-Schutz: gefuelltes Honeypot-Feld oder unrealistisch schneller Submit.
if ($website !== '') {
    redirect_success($redirect);
}

if ($started > 0 && time() - $started < 3) {
    redirect_success($redirect);
}

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
$body .= 'Name:              ' . $name . "\n";
$body .= 'E-Mail:            ' . $email . "\n";
$body .= 'Telefon:           ' . ($phone     !== '' ? $phone     : '-') . "\n";
$body .= 'Anlass:            ' . ($occasion  !== '' ? $occasion  : '-') . "\n";
$body .= 'Wunschdatum:       ' . ($date      !== '' ? $date      : '-') . "\n";
$body .= 'Anzahl Gäste:      ' . ($guests    !== '' ? $guests    : '-') . "\n";
$body .= 'Veranstaltungsort: ' . ($location  !== '' ? $location  : '-') . "\n";
$body .= 'Zeitfenster:       ' . ($timeframe !== '' ? $timeframe : '-') . "\n";
$body .= 'Budget (ca.):      ' . ($budget    !== '' ? $budget    : '-') . "\n";
$body .= 'Ernährung/Allergien: ' . ($dietary  !== '' ? $dietary   : '-') . "\n\n";
$body .= "Nachricht:\n" . ($message !== '' ? $message : '-') . "\n";

// Absender auf eigener Domain (SPF/DMARC-konform), Antwort an Anfragenden.
$headers  = 'From: Jonis Catering Website <info@jonis-catering.de>' . "\r\n";
$headers .= 'Reply-To: ' . $email . "\r\n";
$headers .= 'Content-Type: text/plain; charset=UTF-8' . "\r\n";

// Betreff UTF-8-kodieren (Umlaute korrekt darstellen).
$encodedSubject = encoded_header($subject);

$sent = false;
$smtpConfig = load_smtp_config();
$smtpConfigured = has_smtp_config($smtpConfig);

try {
    $sent = send_via_smtp($to, $subject, $body, $email, $smtpConfig);
} catch (Throwable $exception) {
    error_log('Kontaktformular SMTP-Fehler: ' . $exception->getMessage());
}

if (!$sent && !$smtpConfigured) {
    $sent = @mail($to, $encodedSubject, $body, $headers);
}

// Anfrage zusätzlich an die Google-Sheets-Pipeline melden (Status "Neu").
// Best effort: ohne konfigurierte Webhook-URL passiert einfach nichts.
try {
    notify_sheets_webhook([
        'name' => $name,
        'email' => $email,
        'phone' => $phone,
        'occasion' => $occasion,
        'date' => $date,
        'guests' => $guests,
        'location' => $location,
        'timeframe' => $timeframe,
        'budget' => $budget,
        'dietary' => $dietary,
        'message' => $message,
    ], load_sheets_webhook_config());
} catch (Throwable $exception) {
    error_log('Kontaktformular Sheets-Webhook-Fehler: ' . $exception->getMessage());
}

if ($sent) {
    redirect_success($redirect);
} else {
    header('Location: ' . $redirect . '?error=send#kontakt');
}
exit;
