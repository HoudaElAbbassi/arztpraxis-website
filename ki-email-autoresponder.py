#!/usr/bin/env python3
"""
KI-E-Mail-Autoresponder für Arztpraxis (EINFACHE VERSION - OHNE CalDAV)

Funktion:
1. Liest Terminanfragen per E-Mail (IMAP)
2. KI analysiert die E-Mail (OpenAI GPT-4)
3. Erstellt .ics-Kalenderdatei
4. Sendet automatisch Antwort mit .ics-Anhang

KEIN CalDAV! Nur E-Mail-Automatisierung.
"""

import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
import openai
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

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

# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-preview"  # oder "gpt-3.5-turbo"

# Praxis-Info
PRACTICE_NAME = "Praxis für Gefäßmedizin Remscheid"
PRACTICE_EMAIL = EMAIL_ADDRESS
PRACTICE_PHONE = "+49 123 456 7890"
PRACTICE_ADDRESS = "Musterstraße 123, 12345 Musterstadt"

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

    # Suche ungelesene E-Mails mit "Termin" im Betreff
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
# 2. KI-ANALYSE
# ==========================================

def analyze_with_ai(email_data):
    """KI analysiert Terminanfrage"""
    print(f"\n🤖 KI analysiert E-Mail...")
    print(f"   Von: {email_data['from']}")
    print(f"   Betreff: {email_data['subject']}")

    prompt = f"""
Du bist Assistent für eine Arztpraxis (Gefäßchirurgie & Viszeralchirurgie).

Analysiere diese Terminanfrage und extrahiere Informationen im JSON-Format:

E-Mail:
Von: {email_data['from']}
Betreff: {email_data['subject']}
Text: {email_data['body']}

Heute ist: {datetime.now().strftime('%Y-%m-%d')}

Erstelle JSON:
{{
  "patient_vorname": "...",
  "patient_nachname": "...",
  "patient_email": "...",
  "patient_telefon": "...",
  "wunschtermin_datum": "YYYY-MM-DD",
  "wunschtermin_zeitraum": "morgens|nachmittags|egal",
  "wunschtermin_uhrzeit": "HH:MM oder null",
  "behandlungsgrund": "...",
  "ist_terminanfrage": true/false,
  "dringlichkeit": "normal|dringend|notfall"
}}

Regeln:
- "nächsten Montag" → konkretes Datum
- "vormittags" = morgens
- Falls keine Terminanfrage: ist_terminanfrage = false
"""

    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Du bist ein präziser Daten-Extraktor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        result_text = response.choices[0].message.content

        # JSON extrahieren
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]

        result = json.loads(result_text.strip())

        print(f"✅ Analyse erfolgreich:")
        print(f"   Patient: {result.get('patient_vorname', '?')} {result.get('patient_nachname', '?')}")
        print(f"   Termin: {result.get('wunschtermin_datum', '?')} {result.get('wunschtermin_zeitraum', '?')}")

        return result

    except Exception as e:
        print(f"❌ KI-Fehler: {e}")
        return None


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
        .button {{ display: inline-block; background: #2c5f7c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
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
                <p>Im Anhang dieser E-Mail finden Sie eine Kalenderdatei (.ics), die Sie in Ihren digitalen Kalender importieren können:</p>
                <ul>
                    <li>✅ Microsoft Outlook</li>
                    <li>✅ Apple Kalender</li>
                    <li>✅ Google Kalender</li>
                    <li>✅ Thunderbird</li>
                </ul>
                <p><strong>So geht's:</strong> Öffnen Sie einfach die angehängte Datei, und der Termin wird automatisch in Ihren Kalender übernommen.</p>
            </div>

            <div class="info-box">
                <h3>⚠️ Wichtig:</h3>
                <p>Ihr Termin ist <strong>vorläufig</strong> und wird von uns noch <strong>bestätigt</strong>.</p>
                <p>Wir melden uns in Kürze telefonisch oder per E-Mail bei Ihnen, um den Termin zu bestätigen oder einen alternativen Termin vorzuschlagen.</p>
            </div>

            <h3>📞 Kontakt:</h3>
            <p>
                <strong>Telefon:</strong> {PRACTICE_PHONE}<br>
                <strong>E-Mail:</strong> {PRACTICE_EMAIL}<br>
                <strong>Adresse:</strong> {PRACTICE_ADDRESS}
            </p>

            <p><strong>Sprechzeiten:</strong></p>
            <p>
                Mo-Fr: 08:00-12:00 Uhr<br>
                Mo, Di, Do: 14:00-18:00 Uhr<br>
                Mi & Fr Nachmittag: Geschlossen
            </p>

            <p style="margin-top: 30px;">Mit freundlichen Grüßen,<br>
            Ihr Team der {PRACTICE_NAME}</p>
        </div>

        <div class="footer">
            <p>Diese E-Mail wurde automatisch generiert.</p>
            <p>🤖 Unterstützt durch KI-Technologie</p>
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
    print("🤖 KI-E-Mail-Autoresponder für Arztpraxis")
    print("=" * 70)
    print(f"📧 E-Mail: {EMAIL_ADDRESS}")
    print(f"🏥 Praxis: {PRACTICE_NAME}")
    print("=" * 70)

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

        # KI-Analyse
        analyzed = analyze_with_ai(email_data)

        if not analyzed or not analyzed.get('ist_terminanfrage'):
            print("ℹ️ Keine Terminanfrage, überspringe...")
            continue

        # .ics erstellen
        ics_content, uid = create_ics_file(analyzed)

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
    print("\n✅ Fertig!")


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    # Prüfe Konfiguration
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD nicht gesetzt!")
        print("   Erstelle .env Datei mit: EMAIL_PASSWORD=dein-passwort")
        exit(1)

    if not openai.api_key:
        print("❌ OPENAI_API_KEY nicht gesetzt!")
        print("   Erstelle .env Datei mit: OPENAI_API_KEY=sk-...")
        exit(1)

    # E-Mails verarbeiten
    try:
        process_emails()
    except KeyboardInterrupt:
        print("\n\n⚠️ Abgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
