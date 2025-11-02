# 🚀 Schnellstart - Sicherer E-Mail-Autoresponder

## ⚡ In 5 Minuten einsatzbereit!

### **1. Dependencies installieren**

```bash
cd Arztpraxis
pip3 install -r requirements-sicher.txt
```

### **2. Konfiguration**

```bash
cp .env-sicher.example .env
nano .env
```

Eintragen:
```ini
EMAIL_ADDRESS=houdael@outlook.de
EMAIL_PASSWORD=ihr-passwort
```

### **3. Testen**

```bash
python3 sicherer-email-autoresponder.py
```

### **4. Sicherheits-Check**

```bash
python3 sicherheit.py
# Option 1 wählen: Sicherheits-Check
```

### **5. Automatisierung (optional)**

```bash
crontab -e

# Alle 10 Minuten:
*/10 * * * * cd /pfad/zu/Arztpraxis && python3 sicherer-email-autoresponder.py >> autoresponder.log 2>&1
```

---

## ✅ Fertig!

Ihre Patienten erhalten jetzt automatisch Antworten - **100% DSGVO-konform**!

---

## 📁 Dateien

| Datei | Zweck |
|-------|-------|
| `sicherer-email-autoresponder.py` | Haupt-Script (DSGVO-konform) |
| `sicherheit.py` | Sicherheits-Tool & Wartung |
| `requirements-sicher.txt` | Dependencies (nur 1!) |
| `.env-sicher.example` | Konfigurations-Vorlage |
| `SICHERE-SETUP-ANLEITUNG.md` | Ausführliche Anleitung |
| `DATENSCHUTZ-ANALYSE.md` | DSGVO-Analyse |
| `LÖSUNG-VERGLEICH.md` | OpenAI vs. Sicher |

---

## 🔐 Wichtig

```
✅ Verwenden Sie NUR "sicherer-email-autoresponder.py"
❌ NICHT "ki-email-autoresponder.py" (OpenAI - ILLEGAL!)
```

---

## 📞 Support

Bei Problemen:
1. Schauen Sie in `SICHERE-SETUP-ANLEITUNG.md`
2. Führen Sie Sicherheits-Check aus: `python3 sicherheit.py`
3. Prüfen Sie `.env` Datei

---

**Viel Erfolg! 🚀**
