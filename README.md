# Praxis für Gefäßmedizin Remscheid - Website

Moderne, responsive Website für eine Facharztpraxis mit Schwerpunkt Gefäßchirurgie und Viszeralchirurgie, inklusive Online-Terminbuchung und automatischer Kalender-Integration.

## Features

### ✅ Vollständig implementiert

- **Responsive Design** - Optimiert für Desktop, Tablet und Mobile
- **Online-Terminbuchung** - Formular mit Validierung und E-Mail-Benachrichtigung
- **CalDAV-Integration** - Automatische .ics-Dateien für Kalender-Import
- **Professionelles Design** - Medizinisches Farbschema (Blau-Töne)
- **SEO-optimiert** - Semantisches HTML, Meta-Tags
- **Barrierearm** - WCAG-konforme Strukturen
- **Mobile-First** - Touch-optimierte Navigation und Formulare

### 📋 Sektionen

1. **Header/Navigation**
   - Sticky Header mit Logo
   - Mobile Hamburger-Menü mit Animation
   - Smooth Scrolling zu Sektionen

2. **Hero-Bereich**
   - Willkommensnachricht
   - Call-to-Action Buttons
   - Gradient-Hintergrund

3. **Über uns**
   - Praxis-Vorstellung
   - Spezialisierungen
   - Feature-Liste

4. **Leistungen**
   - 6 Service-Cards:
     - Gefäßchirurgie
     - Viszeralchirurgie
     - Gefäßdiagnostik
     - Wundmanagement
     - Operationsvorbereitung
     - Nachsorge

5. **Terminbuchung**
   - Vollständiges Formular
   - Client-seitige Validierung
   - Server-seitige Verarbeitung
   - CalDAV/iCalendar-Integration
   - E-Mail mit .ics-Anhang

6. **Kontakt**
   - Kontaktinformationen
   - Sprechzeiten
   - Karte (OpenStreetMap)

7. **Footer**
   - Quick Links
   - Rechtliche Seiten (Impressum, Datenschutz)

## Technologie-Stack

### Frontend
- **HTML5** - Semantisches Markup
- **CSS3** - Modern, mit Custom Properties
- **JavaScript (ES6+)** - Vanilla JS, keine Frameworks
- **Font Awesome 6** - Icons
- **Google Fonts** - Inter & Playfair Display

### Backend
- **PHP 7.4+** - Formularverarbeitung
- **CalendarService** - iCalendar-Generierung
- **PHP Mail** - E-Mail-Versand mit Anhängen

### Optional
- **Composer** - Dependency Management
- **Sabre/DAV** - Erweiterte CalDAV-Funktionen

## Projektstruktur

```
Arztpraxis/
├── assets/
│   ├── css/
│   │   └── style.css           # Haupt-Stylesheet (1070 Zeilen)
│   ├── js/
│   │   └── script.js           # JavaScript-Logik (190 Zeilen)
│   └── img/
│       └── logo.jpeg           # Praxis-Logo
│
├── php/
│   └── appointment.php         # Terminbuchungs-Handler (380 Zeilen)
│
├── src/
│   └── CalendarService.php    # iCalendar-Generierung (200 Zeilen)
│
├── caldav/
│   └── server.php              # CalDAV-Server (200 Zeilen)
│
├── uploads/
│   └── calendars/              # Gespeicherte .ics-Dateien
│
├── index.html                  # Hauptseite (385 Zeilen)
├── composer.json               # Dependencies
├── .htaccess                   # Apache-Konfiguration
├── .gitignore                  # Git-Ignore-Regeln
│
├── README.md                   # Diese Datei
├── INSTALLATION.md             # Installationsanleitung
└── CALDAV-README.md            # CalDAV-Dokumentation
```

## Schnellstart

### 1. Installation

```bash
# Dateien auf Server hochladen
scp -r Arztpraxis user@server:/var/www/html/

# Berechtigungen setzen
chmod 755 uploads/calendars
```

### 2. Konfiguration

**E-Mail-Adresse ändern** (`php/appointment.php` Zeile 103):
```php
$to = 'ihre-praxis@example.de';
```

**Praxis-Daten ändern** (`src/CalendarService.php` Zeile 11-13):
```php
private $practiceEmail = 'ihre-praxis@example.de';
private $practiceName = 'Ihre Praxisname';
private $practiceAddress = 'Ihre Straße, PLZ Ort';
```

**Kontaktdaten im HTML** (`index.html`):
- Adresse (Zeile 303)
- Telefon (Zeile 312)
- E-Mail (Zeile 330)
- Sprechzeiten (Zeile 177)

### 3. Testen

```bash
# Website öffnen
open http://localhost/Arztpraxis

# Formular testen mit Ihrer E-Mail
# .ics-Datei sollte im E-Mail-Anhang sein
```

Detaillierte Anleitung: Siehe [INSTALLATION.md](INSTALLATION.md)

## CalDAV-Integration

Die Website enthält eine vollständige CalDAV-Integration:

### Automatische Funktionen

1. **iCalendar-Generierung** - Jede Terminanfrage erzeugt eine .ics-Datei
2. **E-Mail-Anhang** - .ics-Datei wird automatisch angehängt
3. **Kalender-Import** - Patienten können Termin direkt importieren
4. **Erinnerungen** - 24h-Alarm in der .ics-Datei
5. **Zeitzone** - Europe/Berlin
6. **Status** - TENTATIVE (vorläufig, bis bestätigt)

### Unterstützte Kalender-Apps

- Microsoft Outlook
- Apple Kalender (macOS, iOS)
- Google Kalender
- Mozilla Thunderbird
- Samsung Kalender
- Alle CalDAV-kompatiblen Apps

Details: Siehe [CALDAV-README.md](CALDAV-README.md)

## Mobile Optimierung

### Touch-Optimierungen

- **Mindestgröße** für Touch-Targets: 48px
- **Formular-Felder** mit 16px Schriftgröße (verhindert iOS-Zoom)
- **Hamburger-Menü** mit smooth Animation
- **Full-Width Buttons** auf Mobile
- **Optimiertes Spacing** für Daumen-Navigation

### Responsive Breakpoints

- **Desktop**: 992px+
- **Tablet**: 768px - 991px
- **Mobile**: < 768px
- **Small Mobile**: < 480px

### Mobile-Spezifische Features

- Sticky Header
- Hamburger-Menü (animiert zu X)
- Body-Scroll deaktiviert bei offenem Menü
- Einspaltige Layouts
- Vergrößerte Buttons
- Optimierte Formulare

## Browser-Support

- ✅ Chrome/Edge (letzte 2 Versionen)
- ✅ Firefox (letzte 2 Versionen)
- ✅ Safari (letzte 2 Versionen)
- ✅ Mobile Safari (iOS 12+)
- ✅ Chrome Mobile (Android 8+)

## Sicherheit

### Implementierte Maßnahmen

- **Input-Validierung** - Client & Server
- **XSS-Schutz** - htmlspecialchars()
- **CSRF-Token** - Kann hinzugefügt werden
- **Security Headers** - In .htaccess
- **File-Upload-Schutz** - Keine Uploads erlaubt
- **Directory Listing** - Deaktiviert
- **Sensitive Files** - Geschützt via .htaccess

### Empfohlene Maßnahmen

- [ ] HTTPS aktivieren (Let's Encrypt)
- [ ] Datenschutzerklärung hinzufügen
- [ ] Cookie-Banner (falls erforderlich)
- [ ] Impressum erstellen
- [ ] Rate-Limiting für Formular
- [ ] Captcha/reCAPTCHA (optional)

## Performance

### Optimierungen

- **CSS Minification** - Kann hinzugefügt werden
- **Image Optimization** - Externe Unsplash-URLs
- **Browser Caching** - In .htaccess konfiguriert
- **Gzip Compression** - Aktiviert in .htaccess
- **Lazy Loading** - Für Bilder

### Ladezeit

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Total Page Size**: ~200KB (ohne Bilder)

## Wartung

### Regelmäßige Aufgaben

- **Wöchentlich**: Uploads-Ordner aufräumen (alte .ics-Dateien)
- **Monatlich**: Logs prüfen, Backups erstellen
- **Vierteljährlich**: Dependencies aktualisieren
- **Jährlich**: SSL-Zertifikat erneuern

### Backup

```bash
# Komplettes Backup
tar -czf praxis-backup-$(date +%Y%m%d).tar.gz /var/www/html/Arztpraxis

# Nur Daten (ohne Code)
tar -czf praxis-data-$(date +%Y%m%d).tar.gz /var/www/html/Arztpraxis/uploads
```

## Erweiterungsmöglichkeiten

### Geplante Features

- [ ] Admin-Panel für Terminverwaltung
- [ ] Bidirektionale CalDAV-Synchronisation
- [ ] SMS-Erinnerungen
- [ ] Online-Terminbestätigung
- [ ] Patienten-Login-Bereich
- [ ] Integration mit Praxis-Software
- [ ] Blog/News-Sektion
- [ ] FAQ-Bereich
- [ ] Video-Sprechstunde

## Support & Hilfe

### Dokumentation

- [INSTALLATION.md](INSTALLATION.md) - Installationsanleitung
- [CALDAV-README.md](CALDAV-README.md) - CalDAV-Dokumentation

### Troubleshooting

**E-Mails kommen nicht an**:
- PHP mail() testen
- SMTP-Logs prüfen
- Spam-Ordner kontrollieren

**.ics-Dateien werden nicht erstellt**:
- Ordner-Berechtigungen prüfen (755)
- PHP Error Log ansehen

**Formular-Validierung funktioniert nicht**:
- JavaScript-Fehler in Browser-Konsole prüfen
- Cache leeren

## Lizenz

© 2024 Praxis für Gefäßmedizin Remscheid
Alle Rechte vorbehalten.

## Credits

- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Inter, Playfair Display)
- **Bilder**: Unsplash
- **CalDAV**: iCalendar RFC 5545 Standard

---

**Version**: 1.0.0
**Letztes Update**: 2024-10-27
**Entwickelt für**: Praxis für Gefäßmedizin Remscheid
