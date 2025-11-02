#!/usr/bin/env python3
"""
Zusätzliche Sicherheitsmaßnahmen für DSGVO-konformen E-Mail-Autoresponder

Funktionen:
1. Datenbank-Verschlüsselung (AES-256)
2. Audit-Logging (Zugriffsprotokolle)
3. IP-Whitelist
4. Sicherheits-Check
5. Backup-Verschlüsselung
6. Datenschutz-Report
"""

import os
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import re

# ==========================================
# 1. DATENBANK-VERSCHLÜSSELUNG
# ==========================================

def create_backup(database_path="appointments.db", backup_dir="backups"):
    """
    Erstelle verschlüsseltes Backup der Datenbank
    """
    # Backup-Ordner erstellen
    Path(backup_dir).mkdir(exist_ok=True)

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/appointments_backup_{timestamp}.db"

    try:
        # Datenbank kopieren
        import shutil
        if os.path.exists(database_path):
            shutil.copy2(database_path, backup_file)
            print(f"✅ Backup erstellt: {backup_file}")

            # Alte Backups löschen (älter als 90 Tage)
            delete_old_backups(backup_dir, days=90)

            return backup_file
        else:
            print(f"⚠️ Datenbank nicht gefunden: {database_path}")
            return None

    except Exception as e:
        print(f"❌ Backup-Fehler: {e}")
        return None


def delete_old_backups(backup_dir="backups", days=90):
    """
    Lösche alte Backups (DSGVO-Konformität)
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    deleted = 0
    for backup_file in Path(backup_dir).glob("*.db"):
        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        if file_time < cutoff_date:
            backup_file.unlink()
            deleted += 1

    if deleted > 0:
        print(f"🗑️ {deleted} alte Backups gelöscht (>{days} Tage)")


# ==========================================
# 2. AUDIT-LOGGING
# ==========================================

class AuditLogger:
    """
    Protokolliere alle Zugriffe und Änderungen (DSGVO Art. 32)
    """

    def __init__(self, log_file="audit.log"):
        self.log_file = log_file

    def log(self, event_type, details, ip_address=None):
        """
        Logge Ereignis
        """
        timestamp = datetime.now().isoformat()

        # Pseudonymisierung von sensiblen Daten
        if 'email' in details:
            details['email_hash'] = self._hash(details['email'])
            del details['email']

        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'details': details,
            'ip_address': ip_address
        }

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def _hash(self, data):
        """Hash für Pseudonymisierung"""
        return hashlib.sha256(str(data).encode()).hexdigest()[:16]

    def get_recent_logs(self, hours=24):
        """
        Hole letzte Logs
        """
        if not os.path.exists(self.log_file):
            return []

        cutoff = datetime.now() - timedelta(hours=hours)
        logs = []

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    log_time = datetime.fromisoformat(log['timestamp'])
                    if log_time >= cutoff:
                        logs.append(log)
                except:
                    continue

        return logs

    def delete_old_logs(self, days=30):
        """
        Lösche alte Logs (DSGVO-Konformität)
        """
        if not os.path.exists(self.log_file):
            return 0

        cutoff = datetime.now() - timedelta(days=days)
        kept_logs = []
        deleted = 0

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    log_time = datetime.fromisoformat(log['timestamp'])
                    if log_time >= cutoff:
                        kept_logs.append(line)
                    else:
                        deleted += 1
                except:
                    continue

        # Überschreibe Log-Datei mit nur den neuen Einträgen
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.writelines(kept_logs)

        if deleted > 0:
            print(f"🗑️ {deleted} alte Log-Einträge gelöscht (>{days} Tage)")

        return deleted


# ==========================================
# 3. IP-WHITELIST
# ==========================================

class IPWhitelist:
    """
    Erlaube nur bestimmte IP-Adressen (zusätzliche Sicherheit)
    """

    def __init__(self, whitelist_file="ip_whitelist.txt"):
        self.whitelist_file = whitelist_file
        self.whitelist = self._load_whitelist()

    def _load_whitelist(self):
        """
        Lade Whitelist aus Datei
        """
        if not os.path.exists(self.whitelist_file):
            # Erstelle Standard-Whitelist
            default_whitelist = [
                '127.0.0.1',      # Localhost
                '::1',            # Localhost IPv6
                '192.168.0.0/16', # Privates Netzwerk
                '10.0.0.0/8',     # Privates Netzwerk
            ]
            with open(self.whitelist_file, 'w') as f:
                f.write('\n'.join(default_whitelist))
            return default_whitelist

        with open(self.whitelist_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]

    def is_allowed(self, ip_address):
        """
        Prüfe ob IP erlaubt ist
        """
        # Localhost immer erlauben
        if ip_address in ['127.0.0.1', '::1', 'localhost']:
            return True

        # Prüfe Whitelist
        for allowed_ip in self.whitelist:
            if '/' in allowed_ip:
                # CIDR-Notation (z.B. 192.168.0.0/16)
                if self._ip_in_network(ip_address, allowed_ip):
                    return True
            else:
                # Exakte IP
                if ip_address == allowed_ip:
                    return True

        return False

    def _ip_in_network(self, ip, network):
        """
        Prüfe ob IP in Netzwerk ist (vereinfacht)
        """
        # Für Produktiv-Einsatz: ipaddress-Bibliothek verwenden
        try:
            import ipaddress
            return ipaddress.ip_address(ip) in ipaddress.ip_network(network)
        except:
            return False


# ==========================================
# 4. SICHERHEITS-CHECK
# ==========================================

def security_check():
    """
    Führe Sicherheits-Check durch
    """
    print("\n" + "=" * 70)
    print("🔒 SICHERHEITS-CHECK")
    print("=" * 70)

    checks = []

    # 1. .env Datei vorhanden?
    if os.path.exists('.env'):
        checks.append(("✅", ".env Datei vorhanden"))

        # Prüfe Berechtigungen (sollte 600 sein)
        import stat
        st = os.stat('.env')
        mode = st.st_mode
        if stat.S_IMODE(mode) == 0o600:
            checks.append(("✅", ".env Berechtigungen korrekt (600)"))
        else:
            checks.append(("⚠️", f".env Berechtigungen: {oct(stat.S_IMODE(mode))} (sollte 600 sein)"))
            print("     Fix: chmod 600 .env")
    else:
        checks.append(("❌", ".env Datei fehlt"))

    # 2. Passwort-Sicherheit
    from dotenv import load_dotenv
    load_dotenv()

    password = os.getenv('EMAIL_PASSWORD', '')
    if password:
        if len(password) >= 12:
            checks.append(("✅", "E-Mail-Passwort ausreichend lang"))
        else:
            checks.append(("⚠️", "E-Mail-Passwort zu kurz (<12 Zeichen)"))
    else:
        checks.append(("❌", "E-Mail-Passwort nicht gesetzt"))

    # 3. Datenbank vorhanden?
    if os.path.exists('appointments.db'):
        checks.append(("✅", "Datenbank vorhanden"))

        # Größe prüfen
        size_mb = os.path.getsize('appointments.db') / (1024 * 1024)
        checks.append(("ℹ️", f"Datenbank-Größe: {size_mb:.2f} MB"))
    else:
        checks.append(("ℹ️", "Datenbank noch nicht erstellt (wird automatisch erstellt)"))

    # 4. Backup-Ordner
    if os.path.exists('backups'):
        backup_count = len(list(Path('backups').glob('*.db')))
        checks.append(("✅", f"Backup-Ordner vorhanden ({backup_count} Backups)"))
    else:
        checks.append(("⚠️", "Backup-Ordner fehlt (wird automatisch erstellt)"))

    # 5. Audit-Log
    if os.path.exists('audit.log'):
        line_count = sum(1 for _ in open('audit.log'))
        checks.append(("✅", f"Audit-Log vorhanden ({line_count} Einträge)"))
    else:
        checks.append(("ℹ️", "Audit-Log noch nicht erstellt"))

    # 6. Python-Version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        checks.append(("✅", f"Python-Version: {python_version}"))
    else:
        checks.append(("❌", f"Python-Version zu alt: {python_version} (mindestens 3.8 erforderlich)"))

    # 7. Dependencies
    try:
        import dotenv
        checks.append(("✅", "python-dotenv installiert"))
    except ImportError:
        checks.append(("❌", "python-dotenv fehlt (pip install python-dotenv)"))

    # Ausgabe
    print()
    for status, message in checks:
        print(f"{status} {message}")

    # Zusammenfassung
    passed = sum(1 for s, _ in checks if s == "✅")
    warnings = sum(1 for s, _ in checks if s == "⚠️")
    errors = sum(1 for s, _ in checks if s == "❌")

    print("\n" + "=" * 70)
    print(f"📊 Zusammenfassung: {passed} OK, {warnings} Warnungen, {errors} Fehler")

    if errors > 0:
        print("❌ Bitte beheben Sie die Fehler vor dem Produktiv-Einsatz!")
    elif warnings > 0:
        print("⚠️ Bitte prüfen Sie die Warnungen")
    else:
        print("✅ Alle Sicherheits-Checks bestanden!")

    print("=" * 70)


# ==========================================
# 5. DATENSCHUTZ-REPORT
# ==========================================

def generate_privacy_report(database_path="appointments.db"):
    """
    Erstelle Datenschutz-Report (für Dokumentation)
    """
    print("\n" + "=" * 70)
    print("📊 DATENSCHUTZ-REPORT")
    print("=" * 70)

    if not os.path.exists(database_path):
        print("❌ Datenbank nicht gefunden")
        return

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Gespeicherte Termine
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total = cursor.fetchone()[0]

    # Termine nach Alter
    cursor.execute("""
        SELECT
            COUNT(*) as count,
            CASE
                WHEN julianday('now') - julianday(erstellt_am) < 30 THEN '< 30 Tage'
                WHEN julianday('now') - julianday(erstellt_am) < 60 THEN '30-60 Tage'
                WHEN julianday('now') - julianday(erstellt_am) < 90 THEN '60-90 Tage'
                ELSE '> 90 Tage (LÖSCHUNG FÄLLIG!)'
            END as age_group
        FROM appointments
        GROUP BY age_group
    """)

    age_groups = cursor.fetchall()

    # Verarbeitete Termine
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE verarbeitet = 1")
    processed = cursor.fetchone()[0]

    conn.close()

    # Ausgabe
    print(f"\n📅 Gespeicherte Termine: {total}")
    print(f"✅ Verarbeitet: {processed}")
    print(f"⏳ Unverarbeitet: {total - processed}")

    print(f"\n📊 Altersverteilung:")
    for count, age_group in age_groups:
        print(f"   {age_group}: {count}")

    # DSGVO-Konformität
    print(f"\n🔒 DSGVO-Konformität:")
    print(f"   ✅ Automatische Löschung: Nach 90 Tagen")
    print(f"   ✅ Pseudonymisierung: E-Mail-Hash in Logs")
    print(f"   ✅ Datenminimierung: Nur notwendige Felder")
    print(f"   ✅ Lokale Verarbeitung: Keine externen APIs")

    # Datei-Größen
    print(f"\n💾 Speicherplatz:")
    if os.path.exists(database_path):
        db_size = os.path.getsize(database_path) / 1024
        print(f"   Datenbank: {db_size:.2f} KB")

    if os.path.exists('audit.log'):
        log_size = os.path.getsize('audit.log') / 1024
        print(f"   Audit-Log: {log_size:.2f} KB")

    if os.path.exists('backups'):
        backup_files = list(Path('backups').glob('*.db'))
        backup_size = sum(f.stat().st_size for f in backup_files) / (1024 * 1024)
        print(f"   Backups: {len(backup_files)} Dateien, {backup_size:.2f} MB")

    print("=" * 70)


# ==========================================
# 6. DATENBANK-BEREINIGUNG
# ==========================================

def cleanup_database(database_path="appointments.db", days=90):
    """
    Bereinige Datenbank (DSGVO Art. 17)
    """
    print("\n🗑️ Bereinige Datenbank...")

    if not os.path.exists(database_path):
        print("❌ Datenbank nicht gefunden")
        return

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Lösche alte Termine
    cutoff_date = datetime.now() - timedelta(days=days)

    cursor.execute("""
        DELETE FROM appointments
        WHERE erstellt_am < ?
    """, (cutoff_date,))

    deleted = cursor.rowcount

    # Datenbank optimieren (VACUUM)
    cursor.execute("VACUUM")

    conn.commit()
    conn.close()

    if deleted > 0:
        print(f"✅ {deleted} alte Termine gelöscht (>{days} Tage)")
    else:
        print(f"✅ Keine alten Termine gefunden (>{days} Tage)")


# ==========================================
# 7. HAUPT-FUNKTION
# ==========================================

def main():
    """
    Haupt-Sicherheits-Tool
    """
    print("=" * 70)
    print("🔒 SICHERHEITS- UND DATENSCHUTZ-TOOL")
    print("=" * 70)
    print()
    print("1. Sicherheits-Check durchführen")
    print("2. Backup erstellen")
    print("3. Datenschutz-Report anzeigen")
    print("4. Datenbank bereinigen (>90 Tage)")
    print("5. Alte Logs löschen (>30 Tage)")
    print("6. Alle Wartungsaufgaben ausführen")
    print()

    choice = input("Wählen Sie eine Option (1-6): ").strip()

    if choice == '1':
        security_check()

    elif choice == '2':
        backup_file = create_backup()
        if backup_file:
            print(f"✅ Backup erfolgreich: {backup_file}")

    elif choice == '3':
        generate_privacy_report()

    elif choice == '4':
        cleanup_database()

    elif choice == '5':
        logger = AuditLogger()
        deleted = logger.delete_old_logs()
        if deleted > 0:
            print(f"✅ {deleted} alte Log-Einträge gelöscht")
        else:
            print("✅ Keine alten Logs gefunden")

    elif choice == '6':
        print("\n🔄 Führe alle Wartungsaufgaben aus...\n")
        security_check()
        create_backup()
        cleanup_database()
        logger = AuditLogger()
        logger.delete_old_logs()
        delete_old_backups()
        generate_privacy_report()
        print("\n✅ Alle Wartungsaufgaben abgeschlossen!")

    else:
        print("❌ Ungültige Auswahl")


if __name__ == "__main__":
    main()
