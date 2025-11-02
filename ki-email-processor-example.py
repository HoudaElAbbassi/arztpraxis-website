#!/usr/bin/env python3
"""
KI-E-Mail-Processor für Arztpraxis Terminanfragen
Liest E-Mails, analysiert sie mit OpenAI und erstellt CalDAV-Termine
"""

import imaplib
import email
from email.header import decode_header
import openai
import json
from datetime import datetime, timedelta
import caldav
from icalendar import Calendar, Event
import os
from dotenv import load_dotenv

# Konfiguration laden
load_dotenv()

# ==========================================
# Konfiguration
# ==========================================

# E-Mail (IMAP)
EMAIL_SERVER = "outlook.office365.com"  # Für Outlook/Hotmail
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "houdael@outlook.de")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FOLDER = "INBOX"

# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-preview"  # Oder "gpt-3.5-turbo" für günstiger

# CalDAV
CALDAV_URL = os.getenv("CALDAV_URL", "https://ihre-domain.de/caldav/")
CALDAV_USERNAME = os.getenv("CALDAV_USERNAME", "praxis")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")

# Praxis-Einstellungen
PRACTICE_NAME = "Praxis für Gefäßmedizin Remscheid"
PRACTICE_EMAIL = "praxis@beispiel.de"
PRACTICE_ADDRESS = "Musterstraße 123, 12345 Musterstadt"

# Sprechzeiten (für Verfügbarkeits-Prüfung)
OFFICE_HOURS = {
    "monday": {"morning": "08:00-12:00", "afternoon": "14:00-18:00"},
    "tuesday": {"morning": "08:00-12:00", "afternoon": "14:00-18:00"},
    "wednesday": {"morning": "08:00-12:00", "afternoon": None},
    "thursday": {"morning": "08:00-12:00", "afternoon": "14:00-18:00"},
    "friday": {"morning": "08:00-12:00", "afternoon": None},
    "saturday": None,
    "sunday": None
}


# ==========================================
# 1. E-Mail lesen (IMAP)
# ==========================================

def connect_to_email():
    """Verbinde mit E-Mail-Server via IMAP"""
    print(f"🔌 Verbinde mit E-Mail-Server: {EMAIL_SERVER}")

    try:
        imap = imaplib.IMAP4_SSL(EMAIL_SERVER)
        imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print(f"✅ Erfolgreich verbunden als: {EMAIL_ADDRESS}")
        return imap
    except Exception as e:
        print(f"❌ Fehler bei E-Mail-Verbindung: {e}")
        return None


def get_unread_emails(imap):
    """Hole ungelesene E-Mails"""
    imap.select(EMAIL_FOLDER)

    # Suche nach ungelesenen E-Mails
    status, messages = imap.search(None, "UNSEEN")

    if status != "OK":
        print("❌ Fehler beim Abrufen von E-Mails")
        return []

    email_ids = messages[0].split()
    print(f"📧 {len(email_ids)} ungelesene E-Mails gefunden")

    emails = []

    for email_id in email_ids:
        try:
            # Hole E-Mail
            status, msg_data = imap.fetch(email_id, "(RFC822)")

            if status != "OK":
                continue

            # Parse E-Mail
            msg = email.message_from_bytes(msg_data[0][1])

            # Extrahiere Daten
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            from_email = msg.get("From")
            date = msg.get("Date")

            # E-Mail-Body extrahieren
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
                "from": from_email,
                "subject": subject,
                "date": date,
                "body": body
            })

        except Exception as e:
            print(f"⚠️ Fehler beim Parsen von E-Mail {email_id}: {e}")

    return emails


# ==========================================
# 2. KI-Analyse mit OpenAI
# ==========================================

def analyze_email_with_ai(email_data):
    """Analysiere E-Mail-Inhalt mit OpenAI GPT-4"""
    print(f"\n🤖 Analysiere E-Mail mit KI...")
    print(f"   Von: {email_data['from']}")
    print(f"   Betreff: {email_data['subject']}")

    # KI-Prompt
    prompt = f"""
Du bist ein intelligenter Assistent für eine Arztpraxis (Gefäßmedizin und Viszeralchirurgie).

Analysiere die folgende E-Mail-Terminanfrage und extrahiere alle relevanten Informationen.

E-Mail:
Betreff: {email_data['subject']}
Von: {email_data['from']}
Text:
{email_data['body']}

Heutiges Datum: {datetime.now().strftime('%Y-%m-%d')}

Extrahiere bitte folgende Informationen im JSON-Format:

{{
  "intent": "terminbuchung | terminverschiebung | terminabsage | frage | sonstiges",
  "patient": {{
    "vorname": "...",
    "nachname": "...",
    "email": "...",
    "telefon": "..."
  }},
  "wunschtermin": {{
    "datum": "YYYY-MM-DD (oder null wenn nicht angegeben)",
    "zeitraum": "morgens | mittags | nachmittags | abends | egal",
    "uhrzeit_von": "HH:MM (oder null)",
    "uhrzeit_bis": "HH:MM (oder null)",
    "ist_flexibel": true/false
  }},
  "behandlungsgrund": {{
    "kategorie": "gefaesschirurgie | viszeralchirurgie | wundmanagement | nachsorge | erstbesuch | sonstiges",
    "beschreibung": "...",
    "dringlichkeit": "normal | dringend | notfall"
  }},
  "versicherung": {{
    "typ": "gesetzlich | privat | selbstzahler | unbekannt"
  }},
  "zusatzinfo": "Weitere relevante Informationen..."
}}

Regeln:
- Relative Datumsangaben wie "nächsten Montag" in absolutes Datum umwandeln
- "vormittags" = 08:00-12:00, "nachmittags" = 14:00-18:00
- Bei medizinischen Begriffen die passende Kategorie zuordnen
- Dringlichkeit aus Kontext erkennen (Schmerzen, "so schnell wie möglich", etc.)
"""

    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Du bist ein präziser medizinischer Terminassistent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Niedrig für präzise Extraktion
            max_tokens=1000
        )

        # Parse JSON-Antwort
        result_text = response.choices[0].message.content

        # Extrahiere JSON aus Antwort (falls in Markdown-Code-Block)
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        result = json.loads(result_text)

        print("✅ KI-Analyse erfolgreich:")
        print(f"   Intent: {result['intent']}")
        print(f"   Patient: {result['patient']['vorname']} {result['patient']['nachname']}")
        print(f"   Wunschtermin: {result['wunschtermin']['datum']} {result['wunschtermin']['zeitraum']}")
        print(f"   Grund: {result['behandlungsgrund']['kategorie']}")

        return result

    except Exception as e:
        print(f"❌ Fehler bei KI-Analyse: {e}")
        return None


# ==========================================
# 3. Verfügbarkeit prüfen
# ==========================================

def check_availability(wunschtermin):
    """Prüfe ob Wunschtermin verfügbar ist"""
    print(f"\n📅 Prüfe Verfügbarkeit für: {wunschtermin['datum']}")

    # Datum parsen
    termin_datum = datetime.strptime(wunschtermin['datum'], '%Y-%m-%d')
    wochentag = termin_datum.strftime('%A').lower()

    # Deutsche Wochentage
    wochentag_map = {
        'monday': 'Montag',
        'tuesday': 'Dienstag',
        'wednesday': 'Mittwoch',
        'thursday': 'Donnerstag',
        'friday': 'Freitag',
        'saturday': 'Samstag',
        'sunday': 'Sonntag'
    }

    # Prüfe Sprechzeiten
    if wochentag in OFFICE_HOURS and OFFICE_HOURS[wochentag]:
        office_times = OFFICE_HOURS[wochentag]

        # Zeitraum prüfen
        zeitraum = wunschtermin['zeitraum']

        if zeitraum == 'morgens' and office_times.get('morning'):
            print(f"✅ Vormittagstermin möglich: {office_times['morning']}")
            return True, office_times['morning']

        elif zeitraum == 'nachmittags' and office_times.get('afternoon'):
            print(f"✅ Nachmittagstermin möglich: {office_times['afternoon']}")
            return True, office_times['afternoon']

        elif zeitraum == 'egal':
            # Bevorzuge Vormittag
            if office_times.get('morning'):
                print(f"✅ Vormittagstermin möglich: {office_times['morning']}")
                return True, office_times['morning']
            else:
                print(f"✅ Nachmittagstermin möglich: {office_times['afternoon']}")
                return True, office_times['afternoon']

        else:
            print(f"⚠️ Gewünschter Zeitraum nicht verfügbar")
            return False, None
    else:
        print(f"❌ Praxis geschlossen am {wochentag_map.get(wochentag, wochentag)}")
        return False, None


# ==========================================
# 4. CalDAV-Termin erstellen
# ==========================================

def create_caldav_appointment(analyzed_data):
    """Erstelle Termin im CalDAV-Server"""
    print(f"\n📆 Erstelle CalDAV-Termin...")

    try:
        # Verbinde mit CalDAV-Server
        client = caldav.DAVClient(
            url=CALDAV_URL,
            username=CALDAV_USERNAME,
            password=CALDAV_PASSWORD
        )

        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            print("❌ Keine Kalender gefunden")
            return False

        # Hauptkalender verwenden
        calendar = calendars[0]

        # Termin-Details
        patient = analyzed_data['patient']
        wunschtermin = analyzed_data['wunschtermin']
        grund = analyzed_data['behandlungsgrund']

        # Datum & Uhrzeit
        termin_datum = datetime.strptime(wunschtermin['datum'], '%Y-%m-%d')

        # Wenn keine spezifische Uhrzeit, nehme Zeitraum
        if wunschtermin['uhrzeit_von']:
            start_time = datetime.strptime(wunschtermin['uhrzeit_von'], '%H:%M').time()
        else:
            # Default: Vormittags 10:00, Nachmittags 14:00
            if wunschtermin['zeitraum'] == 'nachmittags':
                start_time = datetime.strptime('14:00', '%H:%M').time()
            else:
                start_time = datetime.strptime('10:00', '%H:%M').time()

        # Kombiniere Datum + Zeit
        start_datetime = datetime.combine(termin_datum, start_time)
        end_datetime = start_datetime + timedelta(minutes=30)  # 30 Min Dauer

        # iCalendar Event erstellen
        cal = Calendar()
        event = Event()

        # Eindeutige UID
        uid = f"appointment-{start_datetime.strftime('%Y%m%d-%H%M%S')}-{patient['nachname'].lower()}@praxis.de"
        event.add('uid', uid)

        # Titel
        event.add('summary', f"{patient['vorname']} {patient['nachname']} - {grund['kategorie']}")

        # Beschreibung
        description = f"""
Patient: {patient['vorname']} {patient['nachname']}
Telefon: {patient.get('telefon', 'Nicht angegeben')}
E-Mail: {patient.get('email', 'Nicht angegeben')}
Versicherung: {analyzed_data['versicherung']['typ']}

Behandlungsgrund: {grund['beschreibung']}
Kategorie: {grund['kategorie']}
Dringlichkeit: {grund['dringlichkeit']}

Gebucht via: Online-Terminanfrage (KI-verarbeitet)
"""
        event.add('description', description)

        # Zeiten
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)

        # Status (vorläufig, muss noch bestätigt werden)
        event.add('status', 'TENTATIVE')

        # Ort
        event.add('location', PRACTICE_ADDRESS)

        # Organizer
        event.add('organizer', f'mailto:{PRACTICE_EMAIL}')

        # Attendee (Patient)
        if patient.get('email'):
            event.add('attendee', f'mailto:{patient["email"]}')

        # Custom-Felder für Praxis-Software
        event.add('categories', [grund['kategorie'].upper(), 'ONLINE_BOOKING'])

        # Erinnerung (24h vorher)
        from icalendar import Alarm
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('trigger', timedelta(hours=-24))
        alarm.add('description', f'Termin-Erinnerung: {patient["vorname"]} {patient["nachname"]}')
        event.add_component(alarm)

        cal.add_component(event)

        # In CalDAV-Kalender speichern
        calendar.save_event(cal.to_ical())

        print(f"✅ Termin erfolgreich erstellt:")
        print(f"   UID: {uid}")
        print(f"   Datum: {start_datetime.strftime('%d.%m.%Y %H:%M')}")
        print(f"   Patient: {patient['vorname']} {patient['nachname']}")

        return True, uid

    except Exception as e:
        print(f"❌ Fehler beim Erstellen des CalDAV-Termins: {e}")
        return False, None


# ==========================================
# 5. Bestätigungs-E-Mail senden
# ==========================================

def send_confirmation_email(analyzed_data, termin_uid):
    """Sende Bestätigungs-E-Mail an Patient"""
    print(f"\n📧 Sende Bestätigungs-E-Mail...")

    # TODO: Implementierung mit SMTP
    # Hier würde die E-Mail mit .ics-Anhang gesendet

    patient = analyzed_data['patient']
    wunschtermin = analyzed_data['wunschtermin']

    print(f"✅ Bestätigung würde gesendet an: {patient.get('email', 'Keine E-Mail')}")
    print(f"   Inhalt: Termin am {wunschtermin['datum']} vorläufig bestätigt")

    return True


# ==========================================
# 6. Haupt-Prozess
# ==========================================

def process_appointment_emails():
    """Hauptfunktion: E-Mails verarbeiten"""
    print("=" * 60)
    print("KI-E-Mail-Processor für Arztpraxis-Termine")
    print("=" * 60)

    # 1. Mit E-Mail verbinden
    imap = connect_to_email()
    if not imap:
        return

    # 2. Ungelesene E-Mails holen
    emails = get_unread_emails(imap)

    if not emails:
        print("\n✅ Keine neuen Terminanfragen")
        imap.logout()
        return

    # 3. Jede E-Mail verarbeiten
    for email_data in emails:
        print("\n" + "=" * 60)

        # KI-Analyse
        analyzed = analyze_email_with_ai(email_data)

        if not analyzed:
            print("⚠️ Konnte E-Mail nicht analysieren, überspringe...")
            continue

        # Nur Terminbuchungen verarbeiten
        if analyzed['intent'] != 'terminbuchung':
            print(f"ℹ️ Keine Terminbuchung (Intent: {analyzed['intent']}), überspringe...")
            continue

        # Verfügbarkeit prüfen
        available, time_slot = check_availability(analyzed['wunschtermin'])

        if not available:
            print("⚠️ Wunschtermin nicht verfügbar - manuelle Bearbeitung erforderlich")
            # TODO: Alternative Termine vorschlagen
            continue

        # CalDAV-Termin erstellen
        success, termin_uid = create_caldav_appointment(analyzed)

        if success:
            # Bestätigungs-E-Mail senden
            send_confirmation_email(analyzed, termin_uid)

            # E-Mail als gelesen markieren
            imap.store(email_data['id'].encode(), '+FLAGS', '\\Seen')
            print("✅ E-Mail als gelesen markiert")

        print("=" * 60)

    # 4. Verbindung schließen
    imap.logout()
    print("\n✅ Verarbeitung abgeschlossen")


# ==========================================
# Hauptprogramm
# ==========================================

if __name__ == "__main__":
    # Prüfe Umgebungsvariablen
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD nicht gesetzt!")
        print("   Erstelle .env Datei mit:")
        print("   EMAIL_PASSWORD=dein-passwort")
        exit(1)

    if not openai.api_key:
        print("❌ OPENAI_API_KEY nicht gesetzt!")
        print("   Erstelle .env Datei mit:")
        print("   OPENAI_API_KEY=sk-...")
        exit(1)

    # E-Mails verarbeiten
    process_appointment_emails()
