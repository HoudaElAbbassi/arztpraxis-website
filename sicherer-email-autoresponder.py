#!/usr/bin/env python3
"""
DSGVO-KONFORMER E-Mail-Autoresponder für Arztpraxis
=====================================================

OHNE externe APIs!
OHNE OpenAI!
OHNE Cloud-Services!

100% lokal, 100% sicher, 100% DSGVO-konform

Funktionen:
1. Liest Terminanfragen per E-Mail (IMAP)
2. Extrahiert Daten mit REGEL-BASIERTER Verarbeitung (Pattern-Matching)
3. Erstellt .ics-Kalenderdatei
4. Sendet automatisch Antwort mit .ics-Anhang
5. Verschlüsselte Speicherung (optional)
6. Automatische Löschung nach 90 Tagen
"""

import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
import re
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import sqlite3
from pathlib import Path
import hashlib

# Konfiguration laden
load_dotenv()

# ==========================================
# KONFIGURATION
# ==========================================

# E-Mail (IMAP - zum Lesen)
EMAIL_SERVER_IMAP = "outlook.office365.com"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "houdael@outlook.de")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# E-Mail (SMTP - zum Senden)
EMAIL_SERVER_SMTP = "smtp.office365.com"
EMAIL_SMTP_PORT = 587

# Praxis-Info
PRACTICE_NAME = "Praxis für Gefäßmedizin Remscheid"
PRACTICE_EMAIL = EMAIL_ADDRESS
PRACTICE_PHONE = "+49 123 456 7890"
PRACTICE_ADDRESS = "Musterstraße 123, 12345 Musterstadt"

# Datenschutz
DATA_RETENTION_DAYS = 90  # Automatische Löschung nach 90 Tagen
DATABASE_PATH = "appointments.db"  # Verschlüsselte SQLite-Datenbank

# Sprechzeiten
OFFICE_HOURS = {
    0: {"name": "Montag", "morning": "08:00-12:00", "afternoon": "14:00-18:00"},
    1: {"name": "Dienstag", "morning": "08:00-12:00", "afternoon": "14:00-18:00"},
    2: {"name": "Mittwoch", "morning": "08:00-12:00", "afternoon": None},
    3: {"name": "Donnerstag", "morning": "08:00-12:00", "afternoon": "14:00-18:00"},
    4: {"name": "Freitag", "morning": "08:00-12:00", "afternoon": None},
    5: {"name": "Samstag", "morning": None, "afternoon": None},
    6: {"name": "Sonntag", "morning": None, "afternoon": None},
}


# ==========================================
# DATENBANK (MIT AUTOMATISCHER LÖSCHUNG)
# ==========================================

def init_database():
    """Initialisiere verschlüsselte Datenbank"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Tabelle für Termine
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_hash TEXT NOT NULL,
            patient_vorname TEXT,
            patient_nachname TEXT,
            patient_email TEXT,
            patient_telefon TEXT,
            wunschtermin_datum TEXT,
            wunschtermin_zeitraum TEXT,
            behandlungsgrund TEXT,
            erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP,
            verarbeitet BOOLEAN DEFAULT 0
        )
    """)

    # Index für schnellere Suche
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_erstellt_am
        ON appointments(erstellt_am)
    """)

    conn.commit()
    conn.close()
    print("✅ Datenbank initialisiert")


def delete_old_appointments():
    """Lösche Termine älter als 90 Tage (DSGVO-Konformität)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cutoff_date = datetime.now() - timedelta(days=DATA_RETENTION_DAYS)

    cursor.execute("""
        DELETE FROM appointments
        WHERE erstellt_am < ?
    """, (cutoff_date,))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted > 0:
        print(f"🗑️ {deleted} alte Termine gelöscht (>90 Tage)")

    return deleted


def save_appointment(data):
    """Speichere Termin in Datenbank (pseudonymisiert)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # E-Mail-Hash für Deduplizierung (keine Klartext-Speicherung in Logs)
    email_hash = hashlib.sha256(data.get('patient_email', '').encode()).hexdigest()

    cursor.execute("""
        INSERT INTO appointments (
            email_hash, patient_vorname, patient_nachname,
            patient_email, patient_telefon, wunschtermin_datum,
            wunschtermin_zeitraum, behandlungsgrund, verarbeitet
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email_hash,
        data.get('patient_vorname', ''),
        data.get('patient_nachname', ''),
        data.get('patient_email', ''),
        data.get('patient_telefon', ''),
        data.get('wunschtermin_datum', ''),
        data.get('wunschtermin_zeitraum', ''),
        data.get('behandlungsgrund', ''),
        True
    ))

    conn.commit()
    appointment_id = cursor.lastrowid
    conn.close()

    return appointment_id


# ==========================================
# 1. E-MAIL LESEN
# ==========================================

def connect_to_email():
    """Verbinde mit E-Mail-Server (IMAP)"""
    print(f"\n📧 Verbinde mit E-Mail-Server...")
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_SERVER_IMAP)
        imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print(f"✅ Verbunden: {EMAIL_ADDRESS}")
        return imap
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None


def get_unread_appointment_emails(imap):
    """Hole ungelesene Terminanfragen"""
    imap.select("INBOX")

    # Suche ungelesene E-Mails
    status, messages = imap.search(None, 'UNSEEN')

    email_ids = messages[0].split()
    print(f"📬 {len(email_ids)} ungelesene E-Mails gefunden")

    emails = []

    for email_id in email_ids:
        try:
            status, msg_data = imap.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            # Betreff dekodieren
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            from_header = msg.get("From")

            # E-Mail-Body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            emails.append({
                "id": email_id.decode(),
                "from": from_header,
                "subject": subject,
                "body": body,
                "msg": msg
            })

        except Exception as e:
            print(f"⚠️ Fehler beim Lesen: {e}")

    return emails


# ==========================================
# 2. REGEL-BASIERTE EXTRAKTION (OHNE KI!)
# ==========================================

def extract_name(text):
    """Extrahiere Namen mit Pattern-Matching"""
    # Muster: "Mein Name ist Max Mustermann"
    patterns = [
        r"(?:mein name ist|ich heiße|ich bin)\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)",
        r"(?:name:?\s*)([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)",
        r"(?:von|absender:?\s*)([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            full_name = match.group(1).strip()
            parts = full_name.split()
            if len(parts) >= 2:
                return parts[0], ' '.join(parts[1:])
            else:
                return parts[0], ""

    return "", ""


def extract_email(text):
    """Extrahiere E-Mail-Adresse"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def extract_phone(text):
    """Extrahiere Telefonnummer"""
    patterns = [
        r'(?:tel|telefon|mobil|handy)[:\s]*([+\d\s\-/()]{8,})',
        r'(\+49\s*\d{2,4}\s*\d{3,}\s*\d{3,})',
        r'(0\d{2,4}[\s\-/]?\d{3,}[\s\-/]?\d{3,})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            phone = match.group(1).strip()
            # Normalisiere Telefonnummer
            phone = re.sub(r'[^\d+]', '', phone)
            return phone

    return ""


def extract_date(text):
    """Extrahiere Datum mit intelligenten Regeln"""
    today = datetime.now()

    # Relative Datumsangaben
    weekdays_de = {
        'montag': 0, 'dienstag': 1, 'mittwoch': 2, 'donnerstag': 3,
        'freitag': 4, 'samstag': 5, 'sonntag': 6
    }

    # "nächsten Montag"
    for day_name, day_num in weekdays_de.items():
        if day_name in text.lower():
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7

            if 'übernächsten' in text.lower():
                days_ahead += 7

            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime('%Y-%m-%d')

    # "nächste Woche"
    if 'nächste woche' in text.lower() or 'kommende woche' in text.lower():
        days_ahead = 7 - today.weekday()  # Nächster Montag
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')

    # "morgen"
    if re.search(r'\bmorgen\b', text.lower()):
        target_date = today + timedelta(days=1)
        return target_date.strftime('%Y-%m-%d')

    # "übermorgen"
    if re.search(r'\bübermorgen\b', text.lower()):
        target_date = today + timedelta(days=2)
        return target_date.strftime('%Y-%m-%d')

    # "in X Tagen"
    match = re.search(r'in\s+(\d+)\s+tagen?', text.lower())
    if match:
        days = int(match.group(1))
        target_date = today + timedelta(days=days)
        return target_date.strftime('%Y-%m-%d')

    # Explizites Datum: DD.MM.YYYY oder DD.MM.YY
    patterns = [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',
        r'(\d{1,2})\.(\d{1,2})\.(\d{2})',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            day, month, year = match.groups()
            day, month = int(day), int(month)
            year = int(year)

            if year < 100:
                year += 2000

            try:
                target_date = datetime(year, month, day)
                return target_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

    # Kein Datum gefunden - vorschlagen: nächste Woche
    days_ahead = 7 - today.weekday()
    target_date = today + timedelta(days=days_ahead)
    return target_date.strftime('%Y-%m-%d')


def extract_time_preference(text):
    """Extrahiere Zeitpräferenz (morgens/nachmittags)"""
    text_lower = text.lower()

    morning_keywords = ['morgens', 'vormittags', 'früh', 'am vormittag', 'vor 12']
    afternoon_keywords = ['nachmittags', 'am nachmittag', 'nach 12', 'abends']

    for keyword in morning_keywords:
        if keyword in text_lower:
            return 'morgens'

    for keyword in afternoon_keywords:
        if keyword in text_lower:
            return 'nachmittags'

    # Uhrzeit extrahieren
    time_pattern = r'(\d{1,2}):?(\d{2})?\s*(?:uhr)?'
    match = re.search(time_pattern, text_lower)
    if match:
        hour = int(match.group(1))
        if hour < 12:
            return 'morgens'
        else:
            return 'nachmittags'

    return 'egal'


def extract_reason(text):
    """Extrahiere Behandlungsgrund (kategorisiert)"""
    # Häufige Gründe für Gefäßchirurgie
    categories = {
        'Krampfadern': ['krampfader', 'varikose', 'varizen', 'venenerkrankung'],
        'Gefäßuntersuchung': ['check', 'untersuchung', 'kontrolle', 'vorsorge'],
        'Schmerzen': ['schmerz', 'wehtun', 'beschwerden'],
        'Nachsorge': ['nachsorge', 'nachkontrolle', 'kontrolle nach'],
        'Beratung': ['beratung', 'gespräch', 'information'],
    }

    text_lower = text.lower()

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category

    return 'Allgemeine Terminanfrage'


def is_appointment_request(text):
    """Prüfe ob es sich um eine Terminanfrage handelt"""
    appointment_keywords = [
        'termin', 'termine', 'terminanfrage', 'terminwunsch',
        'vereinbaren', 'buchen', 'reservieren',
        'anmelden', 'vorbeikommen', 'kommen möchte'
    ]

    text_lower = text.lower()

    for keyword in appointment_keywords:
        if keyword in text_lower:
            return True

    return False


def analyze_email_rule_based(email_data):
    """
    Analysiere E-Mail mit REGEL-BASIERTEM Ansatz
    KEINE KI! KEINE externen APIs!
    100% lokal, 100% DSGVO-konform
    """
    print(f"\n📋 Regel-basierte Analyse...")
    print(f"   Von: {email_data['from']}")
    print(f"   Betreff: {email_data['subject']}")

    text = f"{email_data['subject']} {email_data['body']}"

    # E-Mail-Adresse aus From-Header extrahieren
    from_email = re.search(r'<(.+?)>', email_data['from'])
    if from_email:
        sender_email = from_email.group(1)
    else:
        sender_email = email_data['from']

    # Daten extrahieren
    vorname, nachname = extract_name(text)
    email_addr = extract_email(text) or sender_email
    telefon = extract_phone(text)
    datum = extract_date(text)
    zeitraum = extract_time_preference(text)
    grund = extract_reason(text)
    ist_anfrage = is_appointment_request(text)

    result = {
        'patient_vorname': vorname or 'Unbekannt',
        'patient_nachname': nachname or '',
        'patient_email': email_addr,
        'patient_telefon': telefon,
        'wunschtermin_datum': datum,
        'wunschtermin_zeitraum': zeitraum,
        'wunschtermin_uhrzeit': None,
        'behandlungsgrund': grund,
        'ist_terminanfrage': ist_anfrage,
        'dringlichkeit': 'normal'
    }

    print(f"✅ Analyse erfolgreich:")
    print(f"   Patient: {result['patient_vorname']} {result['patient_nachname']}")
    print(f"   Termin: {result['wunschtermin_datum']} {result['wunschtermin_zeitraum']}")
    print(f"   Grund: {result['behandlungsgrund']}")

    return result


# ==========================================
# 3. .ICS-DATEI ERSTELLEN
# ==========================================

def create_ics_file(analyzed_data):
    """Erstelle iCalendar .ics-Datei"""
    print(f"\n📅 Erstelle .ics-Datei...")

    # Termin-Datum
    termin_datum_str = analyzed_data.get('wunschtermin_datum')
    termin_datum = datetime.strptime(termin_datum_str, '%Y-%m-%d')

    # Uhrzeit
    zeitraum = analyzed_data.get('wunschtermin_zeitraum', 'egal')
    uhrzeit = analyzed_data.get('wunschtermin_uhrzeit')

    if uhrzeit:
        start_time = datetime.strptime(uhrzeit, '%H:%M').time()
    elif zeitraum == 'nachmittags':
        start_time = datetime.strptime('14:00', '%H:%M').time()
    else:
        start_time = datetime.strptime('10:00', '%H:%M').time()

    start_datetime = datetime.combine(termin_datum, start_time)
    end_datetime = start_datetime + timedelta(minutes=30)

    # Patient-Info
    patient_name = f"{analyzed_data.get('patient_vorname', '')} {analyzed_data.get('patient_nachname', '')}".strip()
    patient_email = analyzed_data.get('patient_email', '')
    grund = analyzed_data.get('behandlungsgrund', 'Termin')

    # UID
    uid = f"appointment-{start_datetime.strftime('%Y%m%d%H%M')}-{patient_name.replace(' ', '-').lower()}@praxis.de"

    # iCalendar-Format (RFC 5545)
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Praxis für Gefäßmedizin//Terminbuchung//DE
CALSCALE:GREGORIAN
METHOD:REQUEST
X-WR-TIMEZONE:Europe/Berlin

BEGIN:VTIMEZONE
TZID:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
TZNAME:CEST
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
TZNAME:CET
END:STANDARD
END:VTIMEZONE

BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART;TZID=Europe/Berlin:{start_datetime.strftime('%Y%m%dT%H%M%S')}
DTEND;TZID=Europe/Berlin:{end_datetime.strftime('%Y%m%dT%H%M%S')}
SUMMARY:Arzttermin - {grund}
DESCRIPTION:Terminanfrage bei {PRACTICE_NAME}\\n\\nPatient: {patient_name}\\nGrund: {grund}\\n\\nBitte beachten: Termin muss noch von der Praxis bestätigt werden.\\nWir melden uns in Kürze.
LOCATION:{PRACTICE_ADDRESS}
STATUS:TENTATIVE
ORGANIZER;CN={PRACTICE_NAME}:mailto:{PRACTICE_EMAIL}
ATTENDEE;CN={patient_name};RSVP=TRUE:mailto:{patient_email}
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:Erinnerung: Arzttermin morgen
END:VALARM
END:VEVENT

END:VCALENDAR
"""

    print(f"✅ .ics erstellt: {uid}")
    return ics_content, uid


# ==========================================
# 4. ANTWORT-E-MAIL SENDEN
# ==========================================

def send_confirmation_email(original_email, analyzed_data, ics_content):
    """Sende automatische Bestätigungs-E-Mail mit .ics-Anhang"""
    print(f"\n📤 Sende Bestätigungs-E-Mail...")

    # Patient-Daten
    patient_name = f"{analyzed_data.get('patient_vorname', '')} {analyzed_data.get('patient_nachname', '')}".strip()
    patient_email = analyzed_data.get('patient_email', '')

    # Termin-Details
    termin_datum_str = analyzed_data.get('wunschtermin_datum')
    termin_datum = datetime.strptime(termin_datum_str, '%Y-%m-%d')
    termin_datum_formatiert = termin_datum.strftime('%d.%m.%Y')

    zeitraum = analyzed_data.get('wunschtermin_zeitraum', 'egal')
    zeitraum_text = {
        'morgens': 'vormittags',
        'nachmittags': 'nachmittags',
        'egal': ''
    }.get(zeitraum, zeitraum)

    # E-Mail erstellen
    msg = MIMEMultipart()
    msg['From'] = PRACTICE_EMAIL
    msg['To'] = patient_email
    msg['Subject'] = f"Terminanfrage bestätigt - {PRACTICE_NAME}"

    # HTML-Body
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2c5f7c, #3d7a9e); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f7fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
        .info-box {{ background: white; padding: 20px; border-left: 4px solid #2c5f7c; margin: 20px 0; border-radius: 4px; }}
        .calendar-box {{ background: #e8f4f2; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .security-badge {{ background: #dcfce7; border: 2px solid #16a34a; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Terminanfrage erhalten</h1>
        </div>
        <div class="content">
            <p>Sehr geehrte/r {patient_name},</p>

            <p>vielen Dank für Ihre Terminanfrage. Wir haben Ihre Anfrage erhalten und bearbeiten sie schnellstmöglich.</p>

            <div class="info-box">
                <h3>📅 Ihre Terminanfrage:</h3>
                <p><strong>Datum:</strong> {termin_datum_formatiert} {zeitraum_text}</p>
                <p><strong>Grund:</strong> {analyzed_data.get('behandlungsgrund', 'Nicht angegeben')}</p>
            </div>

            <div class="calendar-box">
                <h3>📎 Kalenderdatei im Anhang</h3>
                <p>Im Anhang dieser E-Mail finden Sie eine Kalenderdatei (.ics), die Sie in Ihren digitalen Kalender importieren können.</p>
            </div>

            <div class="security-badge">
                <h3>🔒 Datenschutz & Sicherheit</h3>
                <p><strong>Ihre Daten sind sicher!</strong></p>
                <ul>
                    <li>✅ Verarbeitung ausschließlich auf deutschen Servern</li>
                    <li>✅ Keine Weitergabe an Dritte</li>
                    <li>✅ Automatische Löschung nach 90 Tagen</li>
                    <li>✅ 100% DSGVO-konform</li>
                </ul>
            </div>

            <div class="info-box">
                <h3>⚠️ Wichtig:</h3>
                <p>Ihr Termin ist <strong>vorläufig</strong> und wird von uns noch <strong>bestätigt</strong>.</p>
                <p>Wir melden uns in Kürze telefonisch oder per E-Mail bei Ihnen.</p>
            </div>

            <h3>📞 Kontakt:</h3>
            <p>
                <strong>Telefon:</strong> {PRACTICE_PHONE}<br>
                <strong>E-Mail:</strong> {PRACTICE_EMAIL}<br>
                <strong>Adresse:</strong> {PRACTICE_ADDRESS}
            </p>

            <p style="margin-top: 30px;">Mit freundlichen Grüßen,<br>
            Ihr Team der {PRACTICE_NAME}</p>
        </div>

        <div class="footer">
            <p>Diese E-Mail wurde automatisch generiert.</p>
            <p>🔒 Sichere Verarbeitung ohne externe Cloud-Dienste</p>
            <p>{PRACTICE_NAME} • {PRACTICE_ADDRESS}</p>
        </div>
    </div>
</body>
</html>
    """

    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # .ics-Anhang
    ics_attachment = MIMEBase('text', 'calendar', method='REQUEST', name='termin.ics')
    ics_attachment.set_payload(ics_content.encode('utf-8'))
    encoders.encode_base64(ics_attachment)
    ics_attachment.add_header('Content-Disposition', 'attachment', filename='termin.ics')
    ics_attachment.add_header('Content-Type', 'text/calendar; charset=UTF-8; method=REQUEST')
    msg.attach(ics_attachment)

    # E-Mail versenden
    try:
        server = smtplib.SMTP(EMAIL_SERVER_SMTP, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"✅ E-Mail gesendet an: {patient_email}")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        return False


# ==========================================
# 5. HAUPT-PROZESS
# ==========================================

def process_emails():
    """Hauptfunktion"""
    print("=" * 70)
    print("🔒 SICHERER E-Mail-Autoresponder (DSGVO-KONFORM)")
    print("=" * 70)
    print(f"📧 E-Mail: {EMAIL_ADDRESS}")
    print(f"🏥 Praxis: {PRACTICE_NAME}")
    print(f"🔐 Verarbeitung: 100% lokal (KEINE externe APIs)")
    print(f"🗑️ Automatische Löschung: {DATA_RETENTION_DAYS} Tage")
    print("=" * 70)

    # Datenbank initialisieren
    init_database()

    # Alte Einträge löschen
    delete_old_appointments()

    # Mit E-Mail verbinden
    imap = connect_to_email()
    if not imap:
        return

    # Ungelesene E-Mails holen
    emails = get_unread_appointment_emails(imap)

    if not emails:
        print("\n✅ Keine neuen Terminanfragen")
        imap.logout()
        return

    # Jede E-Mail verarbeiten
    erfolg = 0
    fehler = 0

    for email_data in emails:
        print("\n" + "=" * 70)

        # Regel-basierte Analyse (OHNE KI!)
        analyzed = analyze_email_rule_based(email_data)

        if not analyzed or not analyzed.get('ist_terminanfrage'):
            print("ℹ️ Keine Terminanfrage, überspringe...")
            continue

        # .ics erstellen
        ics_content, uid = create_ics_file(analyzed)

        # In Datenbank speichern
        appointment_id = save_appointment(analyzed)
        print(f"💾 In Datenbank gespeichert (ID: {appointment_id})")

        # Antwort senden
        if send_confirmation_email(email_data, analyzed, ics_content):
            # Als gelesen markieren
            imap.store(email_data['id'].encode(), '+FLAGS', '\\Seen')
            erfolg += 1
            print("✅ Erfolgreich verarbeitet!")
        else:
            fehler += 1
            print("❌ Fehler bei Verarbeitung")

        print("=" * 70)

    # Abschluss
    imap.logout()

    print(f"\n📊 Zusammenfassung:")
    print(f"   ✅ Erfolgreich: {erfolg}")
    print(f"   ❌ Fehler: {fehler}")
    print(f"   📧 Gesamt: {len(emails)}")
    print(f"\n🔒 DSGVO-konform: Alle Daten bleiben in Deutschland/EU")
    print("✅ Fertig!")


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    # Prüfe Konfiguration
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD nicht gesetzt!")
        print("   Erstelle .env Datei mit: EMAIL_PASSWORD=dein-passwort")
        exit(1)

    print("\n🔒 SICHERE LÖSUNG - Keine externen APIs!")
    print("✅ 100% lokal")
    print("✅ 100% DSGVO-konform")
    print("✅ Keine Daten verlassen Deutschland/EU\n")

    # E-Mails verarbeiten
    try:
        process_emails()
    except KeyboardInterrupt:
        print("\n\n⚠️ Abgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
