<?php
/**
 * CalDAV Server Implementation
 * Basic CalDAV server for calendar synchronization
 *
 * This is a simplified implementation. For production use, consider using
 * a full-featured CalDAV server like Sabre/DAV or Baïkal.
 *
 * Requirements:
 * - composer require sabre/dav
 * - Run: composer install
 */

// For production use, install dependencies:
// composer require sabre/dav

/*
// Uncomment when Sabre/DAV is installed via composer

require_once __DIR__ . '/../vendor/autoload.php';

use Sabre\DAV;
use Sabre\CalDAV;

// Calendar storage directory
$calendarDir = __DIR__ . '/../data/calendars';

// Create directory if it doesn't exist
if (!is_dir($calendarDir)) {
    mkdir($calendarDir, 0755, true);
}

// Create backend
$pdo = new PDO('sqlite:' . __DIR__ . '/../data/caldav.db');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Create tables if they don't exist
$pdo->exec("
    CREATE TABLE IF NOT EXISTS calendars (
        id INTEGER PRIMARY KEY,
        principaluri TEXT,
        displayname TEXT,
        uri TEXT,
        description TEXT,
        calendarorder INTEGER,
        calendarcolor TEXT,
        timezone TEXT,
        components TEXT,
        transparent INTEGER
    )
");

$pdo->exec("
    CREATE TABLE IF NOT EXISTS calendarobjects (
        id INTEGER PRIMARY KEY,
        calendardata TEXT,
        uri TEXT,
        calendarid INTEGER,
        lastmodified INTEGER,
        etag TEXT,
        size INTEGER,
        componenttype TEXT,
        firstoccurence INTEGER,
        lastoccurence INTEGER,
        uid TEXT
    )
");

$pdo->exec("
    CREATE TABLE IF NOT EXISTS principals (
        id INTEGER PRIMARY KEY,
        uri TEXT,
        email TEXT,
        displayname TEXT
    )
");

// Insert default principal if not exists
$stmt = $pdo->prepare("SELECT COUNT(*) FROM principals WHERE uri = ?");
$stmt->execute(['principals/praxis']);
if ($stmt->fetchColumn() == 0) {
    $stmt = $pdo->prepare("INSERT INTO principals (uri, email, displayname) VALUES (?, ?, ?)");
    $stmt->execute(['principals/praxis', 'praxis@beispiel.de', 'Praxis für Gefäßmedizin']);
}

// Create backends
$calendarBackend = new CalDAV\Backend\PDO($pdo);
$principalBackend = new DAV\Auth\Backend\PDO($pdo);

// Create calendar root
$tree = [
    new CalDAV\Principal\Collection($principalBackend),
    new CalDAV\CalendarRoot($principalBackend, $calendarBackend)
];

// Create server
$server = new DAV\Server($tree);
$server->setBaseUri('/caldav/');

// Add plugins
$server->addPlugin(new DAV\Auth\Plugin($principalBackend));
$server->addPlugin(new CalDAV\Plugin());
$server->addPlugin(new DAV\Browser\Plugin());
$server->addPlugin(new DAV\Sync\Plugin());

// Run the server
$server->exec();
*/

// ==========================================
// Simplified iCalendar File Server
// (Works without Sabre/DAV installation)
// ==========================================

// Get the request URI
$requestUri = $_SERVER['REQUEST_URI'];
$requestMethod = $_SERVER['REQUEST_METHOD'];

// Parse the request
if (preg_match('/\/caldav\/appointments\/(.+)\.ics$/', $requestUri, $matches)) {
    $appointmentId = $matches[1];
    $icsFile = __DIR__ . '/../uploads/calendars/' . $appointmentId . '.ics';

    if ($requestMethod === 'GET' && file_exists($icsFile)) {
        // Serve the iCalendar file
        header('Content-Type: text/calendar; charset=utf-8');
        header('Content-Disposition: inline; filename="appointment.ics"');
        readfile($icsFile);
        exit;
    } else {
        header('HTTP/1.1 404 Not Found');
        echo 'Calendar file not found';
        exit;
    }
}

// Default response
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>CalDAV Server - Praxis für Gefäßmedizin</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f7fafc;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #2c5f7c; }
        .info { background: #e8f4f2; padding: 15px; border-radius: 6px; margin: 20px 0; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CalDAV Server</h1>
        <p>Willkommen beim CalDAV-Server der Praxis für Gefäßmedizin Remscheid.</p>

        <div class="info">
            <h3>ℹ️ Information</h3>
            <p>Dieser Server ermöglicht die Synchronisation von Terminen mit Ihrem Kalender-Programm.</p>
            <p>Termine werden automatisch als .ics-Dateien per E-Mail zugesendet und können direkt in Ihren Kalender importiert werden.</p>
        </div>

        <h2>Funktionen</h2>
        <ul>
            <li>✅ Automatische iCalendar (.ics) Generierung</li>
            <li>✅ E-Mail mit Kalender-Anhang</li>
            <li>✅ Kompatibel mit allen gängigen Kalender-Apps</li>
            <li>✅ Automatische Erinnerungen (24h vorher)</li>
        </ul>

        <h2>Unterstützte Kalender-Programme</h2>
        <ul>
            <li>Microsoft Outlook</li>
            <li>Apple Kalender (macOS, iOS)</li>
            <li>Google Kalender</li>
            <li>Mozilla Thunderbird</li>
            <li>Alle CalDAV-kompatiblen Apps</li>
        </ul>

        <div class="info">
            <h3>🔧 Erweiterte Funktionen (Optional)</h3>
            <p>Für erweiterte CalDAV-Funktionen mit automatischer Synchronisation installieren Sie:</p>
            <code>composer require sabre/dav</code>
            <p>Danach die auskommentierte Implementierung in dieser Datei aktivieren.</p>
        </div>
    </div>
</body>
</html>
