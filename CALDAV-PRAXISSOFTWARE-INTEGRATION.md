# CalDAV-Integration mit Praxis-Software
## Technische Anleitung für medizinische Software

---

## 🏥 Was ist CalDAV in der Praxis?

**CalDAV** ist der **Standard für Kalender-Synchronisation** in medizinischer Software. Fast alle modernen Praxisverwaltungssysteme (PVS) unterstützen CalDAV.

### Warum CalDAV für Arztpraxen wichtig ist:

```
Online-Terminbuchung
        ↓
    CalDAV-Server
        ↓ ↕ Automatische Synchronisation
  Praxis-Software
  (Ihr PVS-System)
        ↓
Arzt sieht Termin sofort
```

**Ohne CalDAV:**
- ❌ Terminanfragen per E-Mail
- ❌ Manuell übertragen in PVS
- ❌ Fehleranfällig
- ❌ Zeitaufwendig

**Mit CalDAV:**
- ✅ Termin erscheint automatisch im PVS
- ✅ Synchronisation in Echtzeit
- ✅ Keine manuelle Eingabe
- ✅ Keine Doppelbuchungen

---

## 📋 Unterstützte Praxis-Software

### **1. CGM Albis/Albis**

**CalDAV-Support:** ✅ Ja (iCal-Schnittstelle)

**Einrichtung:**
1. Albis öffnen → **Stammdaten** → **Praxis**
2. **iCal-Kalender** aktivieren
3. CalDAV-URL eintragen: `https://ihre-domain.de/caldav/calendars/praxis`
4. Benutzername & Passwort
5. **Synchronisieren** klicken

**Konfiguration:**
```ini
[CalDAV]
server = https://ihre-domain.de/caldav/
username = praxis
password = ********
calendar = praxis-termine
sync_interval = 5 (Minuten)
```

**Synchronisierte Felder:**
- ✅ Patientenname
- ✅ Datum & Uhrzeit
- ✅ Behandlungsgrund
- ✅ Versicherungsstatus
- ✅ Telefonnummer

---

### **2. Medistar**

**CalDAV-Support:** ✅ Ja (mit Plugin)

**Einrichtung:**
1. **Medistar-Admin** öffnen
2. **Module** → **CalDAV-Plugin** installieren
3. **Einstellungen** → **Kalender-Synchronisation**
4. Server-URL: `https://ihre-domain.de/caldav/`
5. Zugangsdaten eingeben
6. Termin-Kategorien zuweisen

**Plugin-Download:**
```
Medistar-Kundenportal → Downloads → Zusatzmodule
→ "iCal/CalDAV Kalender-Integration"
```

**Besonderheiten:**
- Medistar kann mehrere Kalender synchronisieren (ein Kalender pro Arzt)
- Farbliche Kennzeichnung nach Behandlungsart
- Wartelistenfunktion integriert

---

### **3. TurboMed**

**CalDAV-Support:** ✅ Ja (CalDAV-Modul)

**Einrichtung:**
1. TurboMed → **Extras** → **Einstellungen**
2. **Termine** → **Kalender-Synchronisation**
3. **CalDAV-Server hinzufügen**
4. URL: `https://ihre-domain.de/caldav/calendars/hauptkalender/`
5. **Automatische Synchronisation** aktivieren

**Intervall-Einstellung:**
```
Synchronisations-Intervall: 1-60 Minuten
Empfohlen: 5 Minuten
```

**Konflikt-Handling:**
- Bei Doppelbuchung: TurboMed zeigt Warnung
- Manuelle Bestätigung erforderlich
- Alternative Termine werden vorgeschlagen

---

### **4. x.concept (Medistar-Nachfolger)**

**CalDAV-Support:** ✅ Ja (REST-API + iCal)

**Moderne Integration:**
1. x.concept → **System** → **Schnittstellen**
2. **Kalender-Schnittstelle** aktivieren
3. CalDAV-Verbindung konfigurieren
4. **Mapping** definieren (Felder zuordnen)

**REST-API Alternative:**
```javascript
// Direkte Integration via x.concept REST-API
POST https://praxis.x-concept.de/api/v1/appointments
{
  "patient_id": "12345",
  "date": "2024-12-15",
  "time": "10:00",
  "duration": 30,
  "reason": "Kontrolluntersuchung"
}
```

**Vorteile:**
- ✅ Modernste Schnittstelle
- ✅ REST-API für komplexe Integration
- ✅ Webhooks für Echtzeit-Updates

---

### **5. DocCirrus**

**CalDAV-Support:** ✅ Ja (Native Unterstützung)

**Cloud-basiert:**
1. DocCirrus-Dashboard öffnen
2. **Einstellungen** → **Kalender**
3. **Externe Kalender** → **CalDAV hinzufügen**
4. URL: `https://ihre-domain.de/caldav/`
5. Automatische Synchronisation ist immer aktiv

**Cloud-Vorteil:**
- ✅ Keine lokale Installation nötig
- ✅ Von überall erreichbar
- ✅ Automatische Updates
- ✅ Mobile Apps synchronisiert

---

### **6. Tomedo**

**CalDAV-Support:** ✅ Ja (Native CalDAV)

**Mac-fokussiert (da macOS-basiert):**
1. Tomedo → **Einstellungen** → **Kalender**
2. **CalDAV-Account hinzufügen**
3. Server: `https://ihre-domain.de/caldav/`
4. Account-Name: "Online-Terminbuchung"
5. **Fertig**

**Besonderheit:**
- Tomedo nutzt macOS-Kalender-System
- Synchronisiert auch mit Apple Kalender
- iCloud-Integration möglich

---

## 🔧 Technische CalDAV-Einrichtung

### **CalDAV-Server-URLs:**

Ihre Website stellt folgende Endpunkte bereit:

```
Haupt-CalDAV-URL:
https://ihre-domain.de/caldav/

Kalender-URL (Hauptkalender):
https://ihre-domain.de/caldav/calendars/praxis/appointments.ics

Arzt-spezifische Kalender:
https://ihre-domain.de/caldav/calendars/dr-mueller/
https://ihre-domain.de/caldav/calendars/dr-schmidt/
```

### **Authentifizierung:**

```
Methode: HTTP Basic Auth oder OAuth2
Username: praxis
Password: [Ihr sicheres Passwort]
```

### **Unterstützte CalDAV-Methoden:**

```http
PROPFIND   - Kalender abfragen
REPORT     - Termine abrufen
PUT        - Termin erstellen
DELETE     - Termin löschen
```

---

## 📅 iCalendar-Format (RFC 5545)

### Was Ihre PVS-Software empfängt:

```ical
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Praxis für Gefäßmedizin//NONSGML v1.0//EN
CALSCALE:GREGORIAN

BEGIN:VEVENT
UID:appointment-20241215-100000-12345@praxis.de
DTSTAMP:20241201T120000Z
DTSTART:20241215T100000
DTEND:20241215T103000
SUMMARY:Max Mustermann - Kontrolluntersuchung
DESCRIPTION:
 Patient: Max Mustermann
 Geburtsdatum: 01.01.1980
 Versicherung: Gesetzlich
 Telefon: 0151-12345678
 Grund: Kontrolluntersuchung Krampfadern

 Gebucht via Online-Terminbuchung
LOCATION:Praxis für Gefäßmedizin\, Musterstraße 123\, 12345 Musterstadt
STATUS:TENTATIVE
ORGANIZER;CN=Praxis für Gefäßmedizin:mailto:praxis@beispiel.de
ATTENDEE;CN=Max Mustermann;RSVP=TRUE:mailto:max@example.com
CATEGORIES:APPOINTMENT,VASCULAR_SURGERY
X-PATIENT-ID:12345
X-INSURANCE-TYPE:GESETZLICH
X-APPOINTMENT-TYPE:KONTROLLUNTERSUCHUNG
END:VEVENT

END:VCALENDAR
```

### **Custom-Felder (X-Properties):**

Ihre PVS-Software kann diese zusätzlichen Felder auslesen:

```
X-PATIENT-ID        - Patienten-ID aus Ihrer Datenbank
X-INSURANCE-TYPE    - Versicherungstyp (GESETZLICH/PRIVAT)
X-APPOINTMENT-TYPE  - Terminart
X-BOOKING-SOURCE    - Quelle (ONLINE_BOOKING)
X-REQUIRES-CONFIRMATION - Bestätigung erforderlich?
```

---

## 🔄 Bidirektionale Synchronisation

### **Website → Praxis-Software:**

```
1. Patient bucht online
2. CalDAV-Event wird erstellt
3. PVS synchronisiert (5 Min Intervall)
4. Termin erscheint im PVS
```

### **Praxis-Software → Website:**

```
1. Sprechstundenhilfe verschiebt Termin in PVS
2. CalDAV-Event wird aktualisiert
3. Website synchronisiert
4. Patient erhält Update-E-Mail
5. .ics-Datei wird aktualisiert
```

### **Konflikt-Handling:**

Wenn beide Seiten gleichzeitig ändern:

```
Regel 1: PVS hat Vorrang (manuelle Änderung wichtiger)
Regel 2: Website-Änderungen < 5 Min alt → Überschreiben
Regel 3: Bei Konflikt → E-Mail an Admin
```

---

## 🔐 Sicherheit & Zugriffskontrolle

### **Berechtigungen:**

```
Online-Booking-User:
- Kann: Termine erstellen (PUT)
- Kann: Eigene Termine lesen (GET)
- Kann nicht: Termine löschen
- Kann nicht: Andere Termine sehen

Praxis-Admin:
- Kann: Alles
- Kann: Termine bestätigen/ablehnen
- Kann: Termine verschieben/löschen
```

### **Verschlüsselung:**

```
✅ HTTPS/TLS für alle Verbindungen
✅ Verschlüsselte Passwort-Speicherung
✅ Token-basierte Authentifizierung möglich
```

---

## 📊 Monitoring & Logs

### **Was geloggt wird:**

```
[2024-12-15 10:00:00] INFO CalDAV-Sync gestartet
[2024-12-15 10:00:01] INFO Neuer Termin empfangen: appointment-12345
[2024-12-15 10:00:02] INFO Patient: Max Mustermann
[2024-12-15 10:00:03] INFO Datum: 2024-12-20 10:00
[2024-12-15 10:00:04] INFO PVS-Integration erfolgreich
[2024-12-15 10:00:05] SUCCESS Termin in Albis erstellt (ID: 98765)
```

### **Dashboard:**

Sie können ein Admin-Dashboard erstellen mit:

```
- Anzahl Termine heute/Woche/Monat
- Erfolgsrate der Synchronisation
- Fehler-Log
- Letzte Sync-Zeit
- Queue-Status (wartende Termine)
```

---

## 🚨 Fehlerbehandlung

### **Häufige Probleme & Lösungen:**

#### **Problem 1: "Verbindung fehlgeschlagen"**

```
Ursache: Firewall blockiert Port 443
Lösung:
1. Prüfen Sie Firewall-Regeln
2. CalDAV nutzt Port 443 (HTTPS)
3. Whitelist: ihre-domain.de
```

#### **Problem 2: "Authentifizierung fehlgeschlagen"**

```
Ursache: Falsches Passwort oder Benutzername
Lösung:
1. Passwort zurücksetzen
2. Benutzername prüfen (meist: "praxis")
3. Cache in PVS löschen
```

#### **Problem 3: "Doppelbuchungen"**

```
Ursache: Synchronisations-Intervall zu lang
Lösung:
1. Intervall auf 5 Minuten setzen
2. Verfügbarkeits-Prüfung aktivieren
3. Echtzeit-Webhook nutzen (falls verfügbar)
```

#### **Problem 4: "Termin erscheint nicht im PVS"**

```
Ursache: Kalender-URL falsch oder Mapping fehlt
Lösung:
1. CalDAV-URL prüfen
2. Feld-Mapping in PVS kontrollieren
3. Manuelle Synchronisation auslösen
4. Log-Datei prüfen
```

---

## 🎯 Best Practices

### **1. Synchronisations-Intervall:**
```
Empfohlen: 5 Minuten
Minimum: 1 Minute
Maximum: 15 Minuten

Für Echtzeit: Webhooks nutzen (falls PVS unterstützt)
```

### **2. Termin-Status:**
```
TENTATIVE   - Wartet auf Bestätigung (Standard für Online-Buchungen)
CONFIRMED   - Von Praxis bestätigt
CANCELLED   - Abgesagt
```

### **3. Kategorien nutzen:**
```
Gefäßchirurgie   - VASCULAR_SURGERY
Viszeralchirurgie - VISCERAL_SURGERY
Wundmanagement   - WOUND_CARE
Nachsorge        - FOLLOWUP
Erstbesuch       - NEW_PATIENT
```

### **4. Backup:**
```
- Tägliches Backup aller Termine
- Export als .ics-Datei
- Speicherung für 90 Tage
```

---

## 📞 Support-Kontakte

### **Praxis-Software Support:**

**CGM Albis:**
- Tel: 0261 8000-0
- E-Mail: support@cgm.com
- Thema: "CalDAV/iCal-Integration"

**Medistar:**
- Tel: 0711 78 55-0
- E-Mail: support@medistar.de
- Thema: "CalDAV-Plugin"

**TurboMed:**
- Tel: 0911 14 89 70
- E-Mail: support@turbomed.de
- Thema: "Kalender-Synchronisation"

**x.concept:**
- Tel: 0800 7245 300
- E-Mail: support@x-concept.de
- Thema: "REST-API / CalDAV"

---

## 📚 Weitere Ressourcen

**CalDAV-Spezifikation:**
- RFC 4791: https://tools.ietf.org/html/rfc4791

**iCalendar-Format:**
- RFC 5545: https://tools.ietf.org/html/rfc5545

**Test-Tools:**
- CalDAV-Tester: https://caldav.org/
- Thunderbird (CalDAV-Client zum Testen)

---

## ✅ Checkliste für Go-Live

Vor dem produktiven Einsatz:

- [ ] CalDAV-Server aufgesetzt und erreichbar
- [ ] PVS-Software verbunden und Termine synchronisieren
- [ ] Test-Termine erfolgreich übertragen
- [ ] Bidirektionale Sync funktioniert
- [ ] Fehlerbehandlung getestet
- [ ] Backup-System aktiv
- [ ] Team geschult
- [ ] Datenschutz-Dokumentation aktualisiert
- [ ] Patienten-Information erstellt
- [ ] Monitoring aktiviert

---

**Welche Praxis-Software nutzen Sie? Ich kann Ihnen dann spezifische Setup-Anleitung geben!** 🏥
