# KI-gestütztes Terminmanagement - Setup-Anleitung

## 🚀 Schnellstart

```bash
# 1. Repository klonen oder Dateien herunterladen
cd Arztpraxis

# 2. Python-Dependencies installieren
pip install -r requirements.txt

# 3. Konfiguration erstellen
cp .env.example .env
nano .env  # Tragen Sie Ihre Zugangsdaten ein

# 4. Script testen
python ki-email-processor-example.py

# 5. Automatisierung einrichten (Cron)
crontab -e
# Fügen Sie hinzu:
# */5 * * * * cd /pfad/zu/Arztpraxis && python ki-email-processor-example.py
```

---

## 📋 Voraussetzungen

### **1. Python 3.8+**
```bash
# Version prüfen
python --version
# oder
python3 --version
```

### **2. OpenAI API-Key**

1. Gehen Sie zu: https://platform.openai.com/
2. Registrieren/Anmelden
3. **API Keys** → **Create new secret key**
4. Key kopieren: `sk-proj-...`

**Kosten:**
- GPT-4 Turbo: ~$0.01 pro E-Mail (~10€/1000 E-Mails)
- GPT-3.5 Turbo: ~$0.002 pro E-Mail (~2€/1000 E-Mails)

### **3. E-Mail-Zugang (IMAP)**

**Für Outlook/Hotmail:**
- IMAP ist standardmäßig aktiv
- Verwenden Sie Ihr normales Passwort

**Für Gmail:**
1. Google-Konto → Sicherheit
2. **2-Faktor-Authentifizierung** aktivieren
3. **App-Passwörter** erstellen
4. Passwort notieren

### **4. CalDAV-Server** (Optional)

Entweder:
- Ihre Praxis-Software hat CalDAV
- Oder: Radicale/Baïkal installieren (siehe CALDAV-README.md)

---

## ⚙️ Konfiguration

### **1. .env-Datei erstellen**

```bash
cp .env.example .env
```

### **2. E-Mail-Zugangsdaten eintragen**

```ini
EMAIL_SERVER=outlook.office365.com
EMAIL_ADDRESS=houdael@outlook.de
EMAIL_PASSWORD=ihr-passwort-hier
```

**Wichtig:** Niemals .env in Git committen!

### **3. OpenAI API-Key eintragen**

```ini
OPENAI_API_KEY=sk-proj-...
```

### **4. CalDAV konfigurieren** (wenn verfügbar)

```ini
CALDAV_URL=https://ihre-domain.de/caldav/
CALDAV_USERNAME=praxis
CALDAV_PASSWORD=ihr-caldav-passwort
```

---

## 🧪 Testen

### **1. E-Mail-Verbindung testen**

```python
python -c "
from ki_email_processor_example import connect_to_email
imap = connect_to_email()
if imap:
    print('✅ E-Mail-Verbindung funktioniert!')
    imap.logout()
"
```

### **2. OpenAI testen**

```python
python -c "
import openai
openai.api_key = 'sk-...'
response = openai.chat.completions.create(
    model='gpt-4-turbo-preview',
    messages=[{'role': 'user', 'content': 'Hallo'}]
)
print('✅ OpenAI API funktioniert!')
"
```

### **3. Test-E-Mail senden**

Senden Sie sich selbst eine Test-E-Mail:

```
Betreff: Terminanfrage

Hallo,

ich hätte gerne einen Termin am nächsten Montag vormittags.
Mein Name ist Max Mustermann, Tel: 0151-12345678.

Es geht um Krampfadern an beiden Beinen.

Vielen Dank!
```

Dann Script ausführen:
```bash
python ki-email-processor-example.py
```

---

## 🤖 Wie die KI arbeitet

### **Beispiel-E-Mail:**

```
Von: patient@example.com
Betreff: Terminwunsch

Guten Tag,

ich hätte gerne einen Termin nächste Woche Dienstag
nachmittags. Es geht um meine Krampfadern.

Mein Name ist Maria Schmidt, Tel: 0171-9876543

Vielen Dank
```

### **KI extrahiert:**

```json
{
  "intent": "terminbuchung",
  "patient": {
    "vorname": "Maria",
    "nachname": "Schmidt",
    "email": "patient@example.com",
    "telefon": "0171-9876543"
  },
  "wunschtermin": {
    "datum": "2024-12-10",
    "zeitraum": "nachmittags",
    "uhrzeit_von": "14:00",
    "uhrzeit_bis": "18:00",
    "ist_flexibel": true
  },
  "behandlungsgrund": {
    "kategorie": "gefaesschirurgie",
    "beschreibung": "Krampfadern",
    "dringlichkeit": "normal"
  },
  "versicherung": {
    "typ": "unbekannt"
  }
}
```

### **System prüft:**
- ✅ Ist Dienstag nachmittags Sprechzeit?
- ✅ Sind Termine frei?
- ✅ Ist es mehr als 24h in der Zukunft?

### **Wenn verfügbar:**
- ✅ CalDAV-Termin erstellen
- ✅ Bestätigungs-E-Mail an Patient
- ✅ Benachrichtigung an Praxis

---

## 📊 Dashboard (Optional)

### **Einfaches Dashboard mit Flask:**

```bash
pip install flask flask-cors

# dashboard.py erstellen
python dashboard.py

# Browser: http://localhost:5000
```

**Features:**
- Übersicht aller Termine
- Manuelle Bestätigung
- Statistiken
- Log-Ansicht

---

## ⏰ Automatisierung

### **Option 1: Cron (Linux/Mac)**

```bash
# Crontab bearbeiten
crontab -e

# Alle 5 Minuten ausführen
*/5 * * * * cd /pfad/zu/Arztpraxis && /usr/bin/python3 ki-email-processor-example.py >> /var/log/ki-processor.log 2>&1

# Täglich um 8:00 Uhr
0 8 * * * cd /pfad/zu/Arztpraxis && /usr/bin/python3 ki-email-processor-example.py
```

### **Option 2: Systemd Service (Linux)**

```bash
# /etc/systemd/system/ki-processor.service

[Unit]
Description=KI E-Mail Processor für Arztpraxis
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/pfad/zu/Arztpraxis
ExecStart=/usr/bin/python3 /pfad/zu/Arztpraxis/ki-email-processor-example.py
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
```

```bash
# Aktivieren
sudo systemctl enable ki-processor
sudo systemctl start ki-processor

# Status prüfen
sudo systemctl status ki-processor
```

### **Option 3: Windows Task Scheduler**

1. Task Scheduler öffnen
2. **Create Basic Task**
3. Name: "KI E-Mail Processor"
4. Trigger: **Daily** → Repeat every 5 minutes
5. Action: **Start a Program**
   - Program: `python.exe`
   - Arguments: `C:\path\to\ki-email-processor-example.py`
6. Finish

---

## 🔒 Sicherheit

### **1. Passwörter schützen**

```bash
# .env niemals in Git!
echo ".env" >> .gitignore

# Datei-Berechtigungen
chmod 600 .env
```

### **2. Verschlüsselte Speicherung**

```python
# Verwenden Sie python-keyring für Passwörter
import keyring

# Passwort speichern
keyring.set_password("ki-processor", "email", "passwort")

# Passwort abrufen
password = keyring.get_password("ki-processor", "email")
```

### **3. IP-Whitelist** (wenn öffentlich erreichbar)

```python
ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']
```

### **4. Rate Limiting**

```python
# Maximal 100 E-Mails pro Stunde
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=3600)
def process_email(email):
    # ...
```

---

## 📈 Monitoring

### **Log-Datei ansehen:**

```bash
tail -f /var/log/ki-processor.log
```

### **Erfolgsrate messen:**

```python
# Statistiken sammeln
stats = {
    'total_emails': 0,
    'successful': 0,
    'failed': 0,
    'avg_processing_time': 0
}
```

### **Alerting:**

```python
# Bei Fehler E-Mail an Admin
if error_count > 5:
    send_alert_email("admin@praxis.de", "KI-Processor: Zu viele Fehler!")
```

---

## 🐛 Troubleshooting

### **Problem: "Authentication failed"**

**Lösung:**
```bash
# E-Mail-Passwort prüfen
# Bei Gmail: App-Passwort verwenden
# Bei Outlook: Normales Passwort
```

### **Problem: "OpenAI API error"**

**Lösung:**
```bash
# API-Key prüfen
echo $OPENAI_API_KEY

# Guthaben prüfen: https://platform.openai.com/usage
```

### **Problem: "CalDAV connection refused"**

**Lösung:**
```bash
# URL prüfen
curl -I https://ihre-domain.de/caldav/

# Credentials testen
curl -u username:password https://ihre-domain.de/caldav/
```

### **Problem: "Script läuft nicht automatisch"**

**Lösung:**
```bash
# Cron-Log prüfen
grep CRON /var/log/syslog

# Script manuell testen
cd /pfad/zu/Arztpraxis
python ki-email-processor-example.py
```

---

## 💰 Kosten-Übersicht

### **Monatliche Kosten (geschätzt):**

| Position | Kosten/Monat |
|----------|--------------|
| OpenAI API (GPT-4, ~500 E-Mails) | 5€ |
| VPS/Server (optional) | 5€ |
| CalDAV-Hosting (optional) | 0-10€ |
| **Gesamt** | **10-20€** |

### **Zeitersparnis:**

- **Vorher:** 2 Stunden/Tag manuelle Terminverwaltung
- **Nachher:** 15 Minuten/Tag für Kontrolle
- **Ersparnis:** ~35 Stunden/Monat
- **Wert:** ~1.750€/Monat (bei 50€/Stunde)

**ROI:** System bezahlt sich in < 1 Woche!

---

## 🎓 Erweiterungen

### **1. SMS-Benachrichtigung**

```python
# Mit Twilio
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    body="Ihr Termin wurde bestätigt",
    from_='+49...',
    to=patient_phone
)
```

### **2. Automatische Erinnerungen**

```python
# 24h vor Termin
if termin in 24 hours:
    send_reminder_email(patient_email)
    send_reminder_sms(patient_phone)
```

### **3. Video-Sprechstunde-Link**

```python
# Zoom-Meeting erstellen
meeting = zoom_api.create_meeting()
email_body += f"\n\nVideo-Link: {meeting.join_url}"
```

### **4. Multi-Language Support**

```python
# Mit DeepL
from deepl import Translator

translator = Translator(auth_key)
result = translator.translate_text("Termin bestätigt", target_lang="EN")
```

---

## 📚 Ressourcen

**OpenAI:**
- Dokumentation: https://platform.openai.com/docs
- Pricing: https://openai.com/pricing

**CalDAV:**
- RFC 4791: https://tools.ietf.org/html/rfc4791
- Python caldav: https://github.com/python-caldav/caldav

**IMAP:**
- Python imaplib: https://docs.python.org/3/library/imaplib.html

---

## ✅ Checkliste

Vor dem Produktiv-Einsatz:

- [ ] OpenAI API-Key erstellt
- [ ] E-Mail-Zugang funktioniert
- [ ] CalDAV-Server eingerichtet
- [ ] Test-E-Mail erfolgreich verarbeitet
- [ ] Automatisierung eingerichtet (Cron/Systemd)
- [ ] Logging aktiviert
- [ ] Monitoring eingerichtet
- [ ] Team geschult
- [ ] Datenschutz-Dokumentation aktualisiert
- [ ] Patienten informiert (Optional: KI-Verarbeitung)

---

**Viel Erfolg mit Ihrem KI-gestützten Terminmanagement! 🚀**

Bei Fragen: Siehe KI-TERMINMANAGEMENT-KONZEPT.md
