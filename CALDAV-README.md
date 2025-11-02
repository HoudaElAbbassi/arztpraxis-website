# CalDAV Integration - Praxis für Gefäßmedizin

## Übersicht

Die Arztpraxis-Website verfügt über eine vollständige Kalender-Integration, die es Patienten ermöglicht, Termine automatisch in ihre digitalen Kalender zu übernehmen.

## Funktionen

### ✅ Aktuell implementiert

1. **Automatische iCalendar (.ics) Generierung**
   - Jede Terminanfrage erzeugt automatisch eine .ics-Datei
   - Standard-konforme iCalendar-Dateien (RFC 5545)
   - Kompatibel mit allen gängigen Kalender-Programmen

2. **E-Mail mit Kalender-Anhang**
   - Patienten erhalten die .ics-Datei als E-Mail-Anhang
   - Praxis erhält ebenfalls eine Kopie
   - HTML-formatierte E-Mails mit Anleitung

3. **Kalender-Funktionen**
   - Termin-Status: TENTATIVE (vorläufig)
   - Automatische Erinnerung 24h vor dem Termin
   - Zeitzone: Europe/Berlin
   - Standarddauer: 30 Minuten

4. **Datenspeicherung**
   - .ics-Dateien werden in `uploads/calendars/` gespeichert
   - Eindeutige IDs für jeden Termin
   - Archivierung für Nachverfolgung

## Installation

### Basis-Version (ohne Composer)

Die Basis-Implementation funktioniert ohne zusätzliche Dependencies:

```bash
# Erstellen Sie das Upload-Verzeichnis
mkdir -p uploads/calendars
chmod 755 uploads/calendars
```

Die CalendarService-Klasse erstellt .ics-Dateien ohne externe Abhängigkeiten.

### Erweiterte Version (mit Composer - Optional)

Für erweiterte CalDAV-Server-Funktionalität:

```bash
# Installieren Sie Composer-Dependencies
cd Arztpraxis
composer install
```

Dies installiert:
- `sabre/dav` - CalDAV Server-Implementierung
- `sabre/vobject` - iCalendar-Objekt-Handling

## Verwendung

### Für Patienten

1. Patient füllt Terminformular aus
2. System sendet E-Mail mit .ics-Anhang
3. Patient öffnet .ics-Datei
4. Kalender-App öffnet sich automatisch
5. Termin wird importiert (Status: vorläufig)

### Unterstützte Kalender-Programme

- **Microsoft Outlook** (Desktop & Web)
- **Apple Kalender** (macOS, iOS, iPadOS)
- **Google Kalender** (Web & Mobile)
- **Mozilla Thunderbird**
- **Samsung Kalender**
- Alle CalDAV-kompatiblen Apps

## Dateistruktur

```
Arztpraxis/
├── src/
│   └── CalendarService.php       # Kalender-Logik
├── php/
│   └── appointment.php            # Terminbuchungs-Handler
├── caldav/
│   └── server.php                 # CalDAV-Server (optional)
├── uploads/
│   └── calendars/                 # Gespeicherte .ics-Dateien
├── composer.json                  # Dependencies
└── CALDAV-README.md              # Diese Datei
```

## API-Referenz

### CalendarService-Klasse

```php
use Arztpraxis\CalendarService;

$calendar = new CalendarService();

// iCalendar-Inhalt generieren
$icsContent = $calendar->generateICalendar([
    'firstName' => 'Max',
    'lastName' => 'Mustermann',
    'email' => 'max@example.com',
    'appointmentDate' => '2024-12-15',
    'appointmentTime' => '10:00',
    'reason' => 'kontrolluntersuchung'
]);

// Datei speichern
$filepath = $calendar->saveICalendarFile($icsContent, 'termin-123');

// E-Mail-Anhang erstellen
$attachment = $calendar->createEmailAttachment($icsContent, 'termin');
```

## iCalendar-Format

Die generierten .ics-Dateien enthalten:

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Praxis für Gefäßmedizin//Appointment System//DE
METHOD:REQUEST

BEGIN:VEVENT
UID:unique-id@praxis-gefaessmedizin.de
SUMMARY:Arzttermin - Kontrolluntersuchung
DTSTART;TZID=Europe/Berlin:20241215T100000
DTEND;TZID=Europe/Berlin:20241215T103000
LOCATION:Musterstraße 123, 12345 Musterstadt
STATUS:TENTATIVE
ORGANIZER:mailto:praxis@beispiel.de
ATTENDEE:mailto:patient@example.com

BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
END:VALARM

END:VEVENT
END:VCALENDAR
```

## Erweiterte CalDAV-Server-Funktionen (Optional)

### Server-Setup

1. Installieren Sie Dependencies: `composer install`
2. Aktivieren Sie die auskommentierte Implementierung in `caldav/server.php`
3. Konfigurieren Sie Ihren Webserver:

**Apache (.htaccess)**:
```apache
RewriteEngine On
RewriteRule ^caldav/(.*)$ caldav/server.php [L]
```

**Nginx**:
```nginx
location /caldav {
    rewrite ^/caldav/(.*)$ /caldav/server.php last;
}
```

### CalDAV-URL

Nach der Einrichtung können Patienten ihre Kalender abonnieren:
```
https://ihre-domain.de/caldav/calendars/praxis/appointments
```

## Sicherheit

- .ics-Dateien enthalten keine sensiblen medizinischen Daten
- Nur grundlegende Termin-Informationen werden übertragen
- Eindeutige IDs verhindern Duplikate
- STATUS:TENTATIVE zeigt an, dass Termin noch bestätigt werden muss

## Konfiguration

### E-Mail-Adressen anpassen

In `src/CalendarService.php`:

```php
private $practiceEmail = 'ihre-praxis@example.de';
private $practiceName = 'Ihre Praxisname';
private $practiceAddress = 'Ihre Adresse, PLZ Ort';
```

### Termin-Dauer anpassen

Standard: 30 Minuten

```php
// In CalendarService::generateICalendar()
$dateTime->modify('+45 minutes'); // Für 45-Minuten-Termine
```

## Troubleshooting

### Problem: .ics-Datei wird nicht erstellt

**Lösung**: Prüfen Sie Ordner-Berechtigungen
```bash
chmod 755 uploads/calendars
```

### Problem: E-Mail kommt nicht an

**Lösung**: Prüfen Sie PHP mail()-Konfiguration oder verwenden Sie SMTP

### Problem: Termin wird nicht importiert

**Lösung**:
- Prüfen Sie, ob das Datum in der Zukunft liegt
- Stellen Sie sicher, dass die Zeitzone korrekt ist
- Testen Sie mit verschiedenen Kalender-Apps

## Support & Dokumentation

- **iCalendar Spec**: [RFC 5545](https://tools.ietf.org/html/rfc5545)
- **CalDAV Spec**: [RFC 4791](https://tools.ietf.org/html/rfc4791)
- **Sabre/DAV Docs**: [sabre.io/dav](https://sabre.io/dav/)

## Zukünftige Erweiterungen

- [ ] Bidirektionale Synchronisation
- [ ] Terminbestätigung durch Praxis
- [ ] Automatische Terminerinnerungen per SMS
- [ ] Integration mit Praxis-Management-Software
- [ ] Mehrere Kalender (verschiedene Ärzte)
- [ ] Verfügbarkeits-Prüfung in Echtzeit

## Lizenz

© 2024 Praxis für Gefäßmedizin Remscheid
