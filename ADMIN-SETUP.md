# Admin-System Setup-Anleitung

Das Admin-System ermöglicht es, Terminanfragen zu verwalten, anzunehmen oder abzulehnen und Bestätigungs-E-Mails zu versenden.

## Erforderliche Netlify Environment Variables

Gehen Sie zu Ihrer Site auf Netlify: **Site configuration** → **Environment variables**

Fügen Sie folgende Variablen hinzu:

### 1. ADMIN_PASSWORD
**Wert:** Ihr gewünschtes Admin-Passwort (z.B. `SicheresPasswort123!`)
**Beschreibung:** Passwort für den Admin-Login

### 2. NETLIFY_API_TOKEN
**Wert:** Ihr Netlify Personal Access Token

**So erstellen Sie einen Token:**
1. Gehen Sie zu https://app.netlify.com/user/applications
2. Klicken Sie auf **"New access token"**
3. Geben Sie einen Namen ein (z.B. "Admin API")
4. Kopieren Sie den generierten Token
5. Fügen Sie ihn als Environment Variable ein

### 3. SITE_ID
**Wert:** Ihre Netlify Site ID

**So finden Sie Ihre Site ID:**
1. Gehen Sie zu Ihrem Site Dashboard
2. **Site configuration** → **General** → **Site details**
3. Kopieren Sie die **Site ID** (z.B. `abc123-xyz`)

## Optional: E-Mail-Service konfigurieren

Für automatische E-Mail-Benachrichtigungen können Sie einen E-Mail-Service integrieren:

### Option A: SendGrid (Empfohlen)
1. Erstellen Sie einen kostenlosen Account bei SendGrid
2. Holen Sie sich einen API Key
3. Fügen Sie folgende Environment Variables hinzu:
   - `SENDGRID_API_KEY`: Ihr SendGrid API Key
   - `FROM_EMAIL`: Ihre Absender-E-Mail (z.B. `noreply@praxis.de`)

### Option B: SMTP (Alternative)
Konfigurieren Sie SMTP-Credentials in den Environment Variables

## Deployment

Nach dem Hinzufügen der Environment Variables:

1. **Trigger deploy:**
   ```bash
   git push
   ```

2. Oder manuell in Netlify:
   **Deploys** → **Trigger deploy** → **Deploy site**

## Admin-Zugang

Nach dem Deployment:

1. **Login:** https://ihr-site-name.netlify.app/admin.html
2. **Passwort:** Das Passwort, das Sie in `ADMIN_PASSWORD` gesetzt haben
3. **Dashboard:** https://ihr-site-name.netlify.app/admin-dashboard.html (nach Login)

## Funktionen

### Admin Dashboard zeigt:
- ✅ Alle Terminanfragen
- ✅ Status (Offen, Bestätigt, Abgelehnt)
- ✅ Patientendaten
- ✅ Termindetails
- ✅ Statistiken

### Aktionen:
- ✅ Termin bestätigen → Sendet Bestätigungs-E-Mail
- ✅ Termin ablehnen → Sendet Ablehnungs-E-Mail
- ✅ Auto-Refresh alle 60 Sekunden
- ✅ Status wird lokal im Browser gespeichert (localStorage)

## Sicherheitshinweise

1. **Passwort:** Verwenden Sie ein starkes, einzigartiges Passwort
2. **HTTPS:** Admin-Seite ist automatisch via HTTPS geschützt
3. **Session:** Session wird im Browser gespeichert (sessionStorage)
4. **API:** Alle API-Calls benötigen das Admin-Passwort

## Troubleshooting

### Fehler: "Missing Netlify configuration"
- Überprüfen Sie, ob `NETLIFY_API_TOKEN` und `SITE_ID` korrekt gesetzt sind

### Fehler: "Unauthorized"
- Passwort ist falsch oder `ADMIN_PASSWORD` ist nicht gesetzt

### E-Mails werden nicht versendet
- E-Mail-Service (SendGrid) muss noch konfiguriert werden
- Siehe Anleitung oben zur E-Mail-Integration

### Anfragen werden nicht angezeigt
- Überprüfen Sie die Browser-Konsole auf Fehler
- Stellen Sie sicher, dass Netlify Forms korrekt funktioniert

## Support

Bei Problemen:
1. Überprüfen Sie die Netlify Function Logs
2. Überprüfen Sie die Browser-Konsole (F12)
3. Stellen Sie sicher, dass alle Environment Variables korrekt gesetzt sind
