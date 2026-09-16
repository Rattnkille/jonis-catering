<?php
return [
    'host' => 'smtp.hostinger.com',
    'port' => 465,
    'encryption' => 'ssl',
    'username' => 'info@jonis-catering.de',
    'password' => 'HIER_DAS_MAILBOX_PASSWORT_EINTRAGEN',
    'from_email' => 'info@jonis-catering.de',
    'from_name' => 'Jonis Catering Website',

    // Optional: Anfragen zusätzlich an die Google-Sheets-Pipeline melden
    // (siehe sheets-integration/README.md). Ohne diese beiden Werte passiert
    // einfach nichts – die E-Mail-Funktion läuft unabhängig davon weiter.
    'sheets_webhook_url' => '',
    'sheets_webhook_secret' => '',
];
