# Installationsanleitung - Praxis für Gefäßmedizin Website

## Systemanforderungen

- **PHP**: 7.4 oder höher
- **Webserver**: Apache 2.4+ oder Nginx 1.18+
- **E-Mail**: Funktionierende PHP mail() Funktion oder SMTP-Server
- **Speicherplatz**: Mindestens 50MB
- **Optional**: Composer (für erweiterte CalDAV-Funktionen)

## Schnellstart

### 1. Dateien hochladen

Laden Sie alle Dateien auf Ihren Webserver hoch:

```
/var/www/html/praxis/
├── assets/
├── caldav/
├── php/
├── src/
├── uploads/
├── index.html
├── .htaccess
└── composer.json
```

### 2. Berechtigungen setzen

```bash
# Uploads-Verzeichnis beschreibbar machen
chmod 755 uploads
chmod 755 uploads/calendars

# Falls das Verzeichnis nicht existiert
mkdir -p uploads/calendars
chmod 755 uploads/calendars
```

### 3. E-Mail-Konfiguration

Öffnen Sie `php/appointment.php` und ändern Sie:

```php
// Zeile 103 - Ihre Praxis-E-Mail
$to = 'ihre-praxis@example.de';
```

Öffnen Sie `src/CalendarService.php` und aktualisieren Sie:

```php
private $practiceEmail = 'ihre-praxis@example.de';
private $practiceName = 'Ihre Praxisname';
private $practiceAddress = 'Ihre Straße 123, PLZ Ort';
```

### 4. Kontaktdaten anpassen

Öffnen Sie `index.html` und suchen Sie nach folgenden Bereichen:

**Kontaktbereich** (Zeile ~289):
```html
<p>Musterstraße 123<br>12345 Musterstadt</p>
<a href="tel:+491234567890">+49 123 456 7890</a>
<a href="mailto:praxis@beispiel.de">praxis@beispiel.de</a>
```

**Sprechzeiten** (Zeile ~177):
Passen Sie die Sprechzeiten an Ihre Öffnungszeiten an.

**Karte** (Zeile ~335):
Ersetzen Sie die OpenStreetMap-URL mit Ihrer tatsächlichen Adresse.

### 5. Logo anpassen

Ersetzen Sie `assets/img/logo.jpeg` mit Ihrem eigenen Logo.

Unterstützte Formate:
- JPEG (.jpeg, .jpg)
- PNG (.png) - empfohlen für transparenten Hintergrund
- Empfohlene Größe: 500x500px oder höher

## Apache-Konfiguration

### Mod_Rewrite aktivieren

```bash
sudo a2enmod rewrite
sudo systemctl restart apache2
```

### Virtual Host

Erstellen Sie eine Virtual Host Konfiguration:

```apache
<VirtualHost *:80>
    ServerName praxis-gefaessmedizin.de
    ServerAlias www.praxis-gefaessmedizin.de

    DocumentRoot /var/www/html/praxis

    <Directory /var/www/html/praxis>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/praxis-error.log
    CustomLog ${APACHE_LOG_DIR}/praxis-access.log combined
</VirtualHost>
```

### SSL/HTTPS (Empfohlen)

```bash
# Let's Encrypt installieren
sudo apt install certbot python3-certbot-apache

# Zertifikat erstellen
sudo certbot --apache -d praxis-gefaessmedizin.de -d www.praxis-gefaessmedizin.de
```

## Nginx-Konfiguration

```nginx
server {
    listen 80;
    server_name praxis-gefaessmedizin.de www.praxis-gefaessmedizin.de;
    root /var/www/html/praxis;

    index index.html index.php;

    # Disable directory listing
    autoindex off;

    # CalDAV routing
    location /caldav {
        rewrite ^/caldav/(.*)$ /caldav/server.php last;
    }

    # PHP processing
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # Protect sensitive files
    location ~ /\. {
        deny all;
    }

    location ~ ^/(composer\.json|composer\.lock|src/|vendor/) {
        deny all;
    }

    location ~ ^/uploads/calendars/.*\.ics$ {
        deny all;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## PHP Mail-Konfiguration

### Option 1: Standard PHP mail()

Stellen Sie sicher, dass ein MTA (z.B. Postfix) installiert ist:

```bash
sudo apt install postfix
```

### Option 2: SMTP (Empfohlen)

Installieren Sie PHPMailer:

```bash
composer require phpmailer/phpmailer
```

Aktualisieren Sie `php/appointment.php` entsprechend der PHPMailer-Dokumentation.

## CalDAV-Integration (Optional)

### Basis-Version (Standard)

Funktioniert ohne zusätzliche Installation. .ics-Dateien werden per E-Mail versendet.

### Erweiterte Version (mit Sabre/DAV)

```bash
cd /var/www/html/praxis
composer install

# Datenbank-Verzeichnis erstellen
mkdir -p data
chmod 755 data

# CalDAV-Server aktivieren
# Entkommentieren Sie den Code in caldav/server.php
```

## Testen der Installation

### 1. Website aufrufen

```
http://ihre-domain.de
```

### 2. Formular testen

1. Navigieren Sie zu "Termin buchen"
2. Füllen Sie alle Felder aus
3. Verwenden Sie Ihre eigene E-Mail zum Testen
4. Prüfen Sie, ob die E-Mail mit .ics-Anhang ankommt

### 3. Kalender-Import testen

1. Öffnen Sie die empfangene .ics-Datei
2. Ihr Kalender sollte sich öffnen
3. Der Termin sollte als "vorläufig" markiert sein

### 4. CalDAV-Server testen (optional)

```
http://ihre-domain.de/caldav/
```

Sie sollten eine Informationsseite sehen.

## Fehlerbehebung

### E-Mails kommen nicht an

**Problem**: PHP mail() funktioniert nicht

**Lösung**:
```bash
# Prüfen Sie die mail.log
tail -f /var/log/mail.log

# Testen Sie den Mail-Versand
echo "Test" | mail -s "Test Subject" ihre-email@example.de
```

### .ics-Dateien werden nicht erstellt

**Problem**: Uploads-Verzeichnis nicht beschreibbar

**Lösung**:
```bash
chmod 755 uploads/calendars
chown www-data:www-data uploads/calendars
```

### 500 Internal Server Error

**Problem**: .htaccess oder PHP-Fehler

**Lösung**:
```bash
# Apache Error Log prüfen
tail -f /var/log/apache2/error.log

# PHP Errors anzeigen (nur für Entwicklung!)
# In php/appointment.php:
ini_set('display_errors', 1);
```

### CalDAV-URLs funktionieren nicht

**Problem**: mod_rewrite nicht aktiviert

**Lösung**:
```bash
sudo a2enmod rewrite
sudo systemctl restart apache2
```

## Sicherheit

### 1. HTTPS aktivieren

**Immer** SSL/TLS verwenden für Produktionsumgebungen:

```bash
sudo certbot --apache -d ihre-domain.de
```

### 2. Datenschutz

- Erstellen Sie eine Datenschutzerklärung
- Fügen Sie Cookie-Banner hinzu (falls erforderlich)
- DSGVO-Konformität sicherstellen

### 3. Regelmäßige Updates

```bash
# System-Updates
sudo apt update && sudo apt upgrade

# Composer-Dependencies (falls verwendet)
composer update
```

### 4. Backups

```bash
# Tägliches Backup erstellen
tar -czf praxis-backup-$(date +%Y%m%d).tar.gz /var/www/html/praxis
```

## Support

Bei Problemen prüfen Sie:

1. PHP-Version: `php -v`
2. Apache-Module: `apache2ctl -M`
3. Berechtigungen: `ls -la`
4. Error Logs: `/var/log/apache2/error.log`

## Checkliste nach Installation

- [ ] Website erreichbar
- [ ] Alle Links funktionieren
- [ ] Formular sendet E-Mails
- [ ] .ics-Datei im E-Mail-Anhang
- [ ] Kalender-Import funktioniert
- [ ] Kontaktdaten aktualisiert
- [ ] Logo ausgetauscht
- [ ] Sprechzeiten angepasst
- [ ] Karte zeigt korrekten Standort
- [ ] HTTPS aktiviert
- [ ] Datenschutzerklärung hinzugefügt
- [ ] Impressum erstellt

## Produktiv-Schalten

Vor dem Live-Gang:

1. **PHP Error Display deaktivieren**:
   ```php
   // In php/appointment.php
   ini_set('display_errors', 0);
   ```

2. **Sicherheits-Headers aktiviert** (.htaccess)

3. **Backups eingerichtet**

4. **Monitoring aktiviert**

5. **Test-E-Mail an echte Adresse gesendet**

## Weitere Ressourcen

- [PHP.net Dokumentation](https://www.php.net/manual/de/)
- [Apache HTTP Server Docs](https://httpd.apache.org/docs/)
- [CalDAV RFC](https://tools.ietf.org/html/rfc4791)
- [iCalendar RFC](https://tools.ietf.org/html/rfc5545)

---

© 2024 Praxis für Gefäßmedizin Remscheid
