# Arztpraxis Website - Deployment auf Netlify

Diese Website ist eine statische HTML-Seite für eine Arztpraxis mit Terminbuchungsfunktion über Netlify Forms.

## Deployment Schritte

### 1. Repository auf GitHub pushen
```bash
git remote add origin https://github.com/HoudaElAbbassi/arztpraxis-website.git
git push -u origin main
```

### 2. Auf Netlify deployen
1. Gehen Sie zu https://app.netlify.com
2. Klicken Sie auf "Add new site" → "Import an existing project"
3. Wählen Sie "GitHub" und verbinden Sie Ihr Repository
4. Wählen Sie das Repository `arztpraxis-website`
5. Build settings:
   - Build command: (leer lassen)
   - Publish directory: `.` (Punkt)
6. Klicken Sie auf "Deploy site"

### 3. E-Mail-Benachrichtigungen konfigurieren

Nach dem Deployment:

1. Gehen Sie zu **Site configuration** → **Forms**
2. Klicken Sie auf **Form notifications**
3. Klicken Sie auf **Add notification** → **Email notification**
4. Konfigurieren Sie:
   - **Event to listen for**: New form submission
   - **Form**: `terminanfrage`
   - **Email to notify**: `houdael@outlook.de` (oder Ihre gewünschte E-Mail)
   - **Email subject**: `Neue Terminanfrage von {firstName} {lastName}`

5. **Optional**: Aktivieren Sie **Spam filtering** um Spam zu reduzieren

### 4. Custom Domain (Optional)

Falls Sie eine eigene Domain verbinden möchten:
1. Gehen Sie zu **Site configuration** → **Domain management**
2. Klicken Sie auf **Add domain alias**
3. Geben Sie Ihre Domain ein (z.B. `www.praxis-gefaessmedizin.de`)
4. Folgen Sie den DNS-Konfigurationsanweisungen

## Formular-Daten einsehen

Alle eingegangenen Terminanfragen können Sie in Netlify einsehen:

1. Gehen Sie zu **Forms** im Netlify Dashboard
2. Klicken Sie auf das Formular `terminanfrage`
3. Dort sehen Sie alle Submissions mit allen Details

Sie können die Daten auch als CSV exportieren.

## Features

- ✅ Responsive Design für alle Geräte
- ✅ Netlify Forms für Terminanfragen
- ✅ Spam-Schutz mit Honeypot
- ✅ E-Mail-Benachrichtigungen bei neuen Anfragen
- ✅ Automatische Form-Validierung
- ✅ Smooth Scrolling Navigation
- ✅ Mobile-friendly Navigation

## Anpassungen

### Logo austauschen
- Ersetzen Sie `/assets/img/logo.jpeg` mit Ihrem Logo

### Kontaktdaten ändern
- Öffnen Sie `index.html`
- Suchen Sie nach "Musterstraße" und ersetzen Sie die Platzhalter mit echten Daten

### Öffnungszeiten anpassen
- In `index.html` im Contact Section

### E-Mail-Adresse für Benachrichtigungen
- Wird in den Netlify Form-Einstellungen konfiguriert (siehe oben)

## Support

Bei Fragen oder Problemen:
- Netlify Docs: https://docs.netlify.com/forms/setup/
- GitHub Issues: https://github.com/HoudaElAbbassi/arztpraxis-website/issues
