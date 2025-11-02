# KI-E-Mail-Autoresponder - Einfache Setup-Anleitung

## 🎯 Was macht das System?

```
Patient sendet E-Mail
    ↓
KI liest & analysiert (5 Sekunden)
    ↓
Automatische Antwort mit .ics-Datei
    ↓
FERTIG!
```

**Kein CalDAV! Kein kompliziertes Setup! Nur E-Mail.**

---

## ⚡ Schnellstart (5 Minuten)

### **Schritt 1: Python installieren**

```bash
# Prüfen ob Python installiert ist
python3 --version

# Falls nicht: https://python.org/ (Python 3.8+)
```

### **Schritt 2: Dateien vorbereiten**

```bash
cd Arztpraxis

# Dependencies installieren
pip3 install -r requirements-simple.txt
```

### **Schritt 3: Konfiguration**

```bash
# Kopiere Vorlage
cp .env-simple.example .env

# Bearbeiten
nano .env
```

Tragen Sie ein:
```ini
EMAIL_ADDRESS=houdael@outlook.de
EMAIL_PASSWORD=ihr-passwort
OPENAI_API_KEY=sk-proj-...
```

### **Schritt 4: OpenAI API-Key holen**

1. Gehen Sie zu: https://platform.openai.com/
2. Registrieren (kostenlos)
3. **API Keys** → **Create new secret key**
4. Key kopieren: `sk-proj-...`
5. In `.env` eintragen

**Kosten:** ~$0.01 pro E-Mail (~10€ für 1000 E-Mails)

### **Schritt 5: Testen!**

```bash
# Script ausführen
python3 ki-email-autoresponder.py
```

---

## 📧 Wie es funktioniert

### **1. Patient sendet E-Mail:**

```
An: houdael@outlook.de
Betreff: Terminwunsch

Hallo,

ich hätte gerne einen Termin nächste Woche Montag vormittags.
Mein Name ist Max Mustermann, Tel: 0151-12345678.
Es geht um Krampfadern.

Vielen Dank!
```

### **2. KI analysiert automatisch:**

```json
{
  "patient_vorname": "Max",
  "patient_nachname": "Mustermann",
  "patient_email": "max@example.com",
  "patient_telefon": "0151-12345678",
  "wunschtermin_datum": "2024-12-09",
  "wunschtermin_zeitraum": "morgens",
  "behandlungsgrund": "Krampfadern",
  "ist_terminanfrage": true
}
```

### **3. Patient erhält automatisch:**

✅ **Bestätigungs-E-Mail** (schönes HTML-Design)
✅ **.ics-Kalenderdatei** im Anhang
✅ Termin kann direkt importiert werden

---

## ⚙️ Automatisierung einrichten

### **Option 1: Cron (Mac/Linux) - Empfohlen**

```bash
# Crontab bearbeiten
crontab -e

# Alle 10 Minuten prüfen
*/10 * * * * cd /pfad/zu/Arztpraxis && python3 ki-email-autoresponder.py

# Oder jede Stunde
0 * * * * cd /pfad/zu/Arztpraxis && python3 ki-email-autoresponder.py
```

### **Option 2: While-Loop (immer laufen)**

```bash
# Script erstellt das automatisch ausführen
while true; do
    python3 ki-email-autoresponder.py
    echo "⏳ Warte 10 Minuten..."
    sleep 600
done
```

### **Option 3: Windows Task Scheduler**

1. **Task Scheduler** öffnen
2. **Create Basic Task**
3. Name: "KI E-Mail Autoresponder"
4. Trigger: **Repeat every 10 minutes**
5. Action: `python.exe ki-email-autoresponder.py`

---

## 📋 Was brauche ich?

### **Zwingend erforderlich:**
- ✅ Python 3.8+
- ✅ E-Mail-Adresse (Outlook/Gmail)
- ✅ OpenAI API-Key (~10€/Monat)

### **NICHT erforderlich:**
- ❌ Kein Server nötig (läuft lokal!)
- ❌ Kein CalDAV
- ❌ Keine Datenbank
- ❌ Keine Praxis-Software-Integration

**Total: ~10€/Monat (nur OpenAI)**

---

## 🔐 Sicherheit

### **Passwörter schützen:**

```bash
# .env niemals teilen oder committen!
chmod 600 .env
```

### **Gmail-Nutzer:**

Gmail benötigt ein **App-Passwort** (nicht Ihr normales Passwort):

1. Google-Konto → **Sicherheit**
2. **2-Faktor-Authentifizierung** aktivieren
3. **App-Passwörter** erstellen
4. Passwort notieren und in `.env` eintragen

---

## 🧪 Testen

### **Test-E-Mail senden:**

Senden Sie sich selbst eine Test-E-Mail:

```
An: houdael@outlook.de
Betreff: Terminanfrage Test

Hallo,

ich möchte gerne einen Termin am 20.12.2024 vormittags.
Mein Name ist Test Patient.
Tel: 0123-456789

Danke!
```

### **Script ausführen:**

```bash
python3 ki-email-autoresponder.py
```

### **Erwartete Ausgabe:**

```
======================================================================
🤖 KI-E-Mail-Autoresponder für Arztpraxis
======================================================================
📧 E-Mail: houdael@outlook.de
🏥 Praxis: Praxis für Gefäßmedizin Remscheid
======================================================================

📧 Verbinde mit E-Mail-Server...
✅ Verbunden: houdael@outlook.de
📬 1 ungelesene E-Mails gefunden

======================================================================

🤖 KI analysiert E-Mail...
   Von: test@example.com
   Betreff: Terminanfrage Test
✅ Analyse erfolgreich:
   Patient: Test Patient
   Termin: 2024-12-20 morgens

📅 Erstelle .ics-Datei...
✅ .ics erstellt: appointment-20241220-test-patient@praxis.de

📤 Sende Bestätigungs-E-Mail...
✅ E-Mail gesendet an: test@example.com
✅ Erfolgreich verarbeitet!
======================================================================

📊 Zusammenfassung:
   ✅ Erfolgreich: 1
   ❌ Fehler: 0
   📧 Gesamt: 1

✅ Fertig!
```

---

## 📊 Beispiel-E-Mail die Patient erhält

**Betreff:** Terminanfrage bestätigt - Praxis für Gefäßmedizin Remscheid

**Inhalt:**
```
Sehr geehrte/r Max Mustermann,

vielen Dank für Ihre Terminanfrage. Wir haben Ihre Anfrage
erhalten und bearbeiten sie schnellstmöglich.

📅 Ihre Terminanfrage:
Datum: 09.12.2024 vormittags
Grund: Krampfadern

📎 Kalenderdatei im Anhang
Im Anhang finden Sie eine .ics-Datei zum Import in Ihren Kalender.

⚠️ Wichtig:
Ihr Termin ist vorläufig und wird von uns noch bestätigt.
Wir melden uns in Kürze bei Ihnen.

Mit freundlichen Grüßen,
Ihr Team der Praxis für Gefäßmedizin Remscheid
```

**Anhang:** `termin.ics` (Kalenderdatei)

---

## ⚡ Vorteile dieser Lösung

### **✅ Super einfach:**
- Nur 2 Dependencies (OpenAI + python-dotenv)
- Keine komplexe Installation
- Läuft lokal auf Ihrem Computer
- Keine Server nötig

### **✅ Kostengünstig:**
- ~10€/Monat (nur OpenAI API)
- Keine CalDAV-Server-Kosten
- Keine Hosting-Kosten

### **✅ Sofort nutzbar:**
- Setup in 5 Minuten
- Kein Warten auf IT-Abteilung
- Keine Praxis-Software-Integration nötig

### **✅ Flexibel:**
- Läuft auf Mac/Windows/Linux
- Kann später zu CalDAV erweitert werden
- Jederzeit anpassbar

---

## 🚀 Erweiterte Features (später)

Diese Lösung kann später erweitert werden mit:

- 📊 **Dashboard** (Übersicht alle Anfragen)
- 📱 **SMS-Benachrichtigung** (mit Twilio)
- 📅 **CalDAV-Integration** (mit Praxis-Software)
- 🤝 **CRM-Integration** (Patientenverwaltung)
- 📈 **Statistiken** (Wie viele Anfragen/Tag?)

Aber erstmal: **Keep it simple!** ✨

---

## 🐛 Probleme lösen

### **"Authentication failed"**
```bash
# Passwort prüfen
# Gmail: App-Passwort verwenden!
# Outlook: Normales Passwort
```

### **"OpenAI API error"**
```bash
# API-Key prüfen
# Guthaben prüfen: https://platform.openai.com/usage
```

### **"No module named 'openai'"**
```bash
pip3 install -r requirements-simple.txt
```

### **"Permission denied"**
```bash
chmod +x ki-email-autoresponder.py
```

---

## 💡 Tipps

### **1. Erst testen, dann automatisieren:**
- Führen Sie das Script erstmal manuell aus
- Senden Sie Test-E-Mails
- Wenn alles funktioniert → Cron einrichten

### **2. Log-Datei erstellen:**
```bash
python3 ki-email-autoresponder.py >> autoresponder.log 2>&1
```

### **3. Praxis-Info anpassen:**
Bearbeiten Sie `ki-email-autoresponder.py` Zeile 32-35:
```python
PRACTICE_NAME = "Ihre Praxisname"
PRACTICE_PHONE = "+49 ..."
PRACTICE_ADDRESS = "Ihre Adresse"
```

---

## 📞 Support

**Bei Problemen:**
1. Prüfen Sie `.env` Datei (Passwörter korrekt?)
2. Testen Sie OpenAI API separat
3. Schauen Sie in `autoresponder.log`

**OpenAI Hilfe:**
- https://platform.openai.com/docs

---

## ✅ Checkliste

Vor dem ersten Einsatz:

- [ ] Python 3.8+ installiert
- [ ] `requirements-simple.txt` installiert
- [ ] `.env` Datei erstellt und ausgefüllt
- [ ] OpenAI API-Key funktioniert
- [ ] Test-E-Mail erfolgreich verarbeitet
- [ ] Automatische Antwort kam an
- [ ] .ics-Datei lässt sich öffnen
- [ ] Praxis-Info angepasst (Name, Telefon, Adresse)
- [ ] Sprechzeiten korrekt (im Code)

---

## 🎉 Fertig!

**Das war's! So einfach kann KI-Automatisierung sein.**

Ihre Patienten erhalten jetzt innerhalb von **Minuten** eine professionelle Antwort mit Kalenderdatei - **vollautomatisch**! 🚀

---

**Fragen? Schauen Sie in die anderen Dokumentationen:**
- `KI-TERMINMANAGEMENT-KONZEPT.md` - Detailliertes Konzept
- `KI-INTEGRATION-README.md` - Erweiterte Version mit CalDAV
