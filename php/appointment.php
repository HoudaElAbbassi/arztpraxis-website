<?php
/**
 * Arztpraxis - Appointment Booking Handler
 * Processes appointment form submissions and sends email notifications
 * Includes CalDAV integration for calendar synchronization
 */

// Set JSON response header
header('Content-Type: application/json');

// Enable error reporting for development (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 0);

// Load CalendarService
require_once __DIR__ . '/../src/CalendarService.php';
use Arztpraxis\CalendarService;

// Function to sanitize input data
function sanitize_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// Check if request is POST
if ($_SERVER["REQUEST_METHOD"] != "POST") {
    echo json_encode([
        'success' => false,
        'message' => 'Ungültige Anfrage.'
    ]);
    exit;
}

// Validate and sanitize form data
$firstName = sanitize_input($_POST['firstName'] ?? '');
$lastName = sanitize_input($_POST['lastName'] ?? '');
$birthdate = sanitize_input($_POST['birthdate'] ?? '');
$insurance = sanitize_input($_POST['insurance'] ?? '');
$email = sanitize_input($_POST['email'] ?? '');
$phone = sanitize_input($_POST['phone'] ?? '');
$appointmentDate = sanitize_input($_POST['appointmentDate'] ?? '');
$appointmentTime = sanitize_input($_POST['appointmentTime'] ?? '');
$reason = sanitize_input($_POST['reason'] ?? '');
$message = sanitize_input($_POST['message'] ?? '');
$privacy = isset($_POST['privacy']) ? true : false;

// Validate required fields
$errors = [];

if (empty($firstName)) {
    $errors[] = 'Vorname ist erforderlich.';
}

if (empty($lastName)) {
    $errors[] = 'Nachname ist erforderlich.';
}

if (empty($birthdate)) {
    $errors[] = 'Geburtsdatum ist erforderlich.';
}

if (empty($insurance)) {
    $errors[] = 'Versicherungsart ist erforderlich.';
}

if (empty($email)) {
    $errors[] = 'E-Mail ist erforderlich.';
} elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'Ungültige E-Mail-Adresse.';
}

if (empty($phone)) {
    $errors[] = 'Telefonnummer ist erforderlich.';
}

if (empty($appointmentDate)) {
    $errors[] = 'Wunschtermin ist erforderlich.';
} else {
    // Check if date is not in the past
    $selectedDate = strtotime($appointmentDate);
    $today = strtotime(date('Y-m-d'));
    if ($selectedDate < $today) {
        $errors[] = 'Das Datum darf nicht in der Vergangenheit liegen.';
    }
}

if (empty($reason)) {
    $errors[] = 'Grund des Besuchs ist erforderlich.';
}

if (!$privacy) {
    $errors[] = 'Sie müssen die Datenschutzerklärung akzeptieren.';
}

// Return errors if validation failed
if (!empty($errors)) {
    echo json_encode([
        'success' => false,
        'message' => implode(' ', $errors)
    ]);
    exit;
}

// ==========================================
// Prepare Email Content
// ==========================================

// Practice email (CHANGE THIS TO YOUR ACTUAL EMAIL)
$to = 'houdael@outlook.de';

// Email subject
$subject = 'Neue Terminanfrage: ' . $firstName . ' ' . $lastName;

// Translate insurance type
$insuranceTypes = [
    'gesetzlich' => 'Gesetzlich versichert',
    'privat' => 'Privat versichert',
    'selbstzahler' => 'Selbstzahler'
];
$insuranceText = $insuranceTypes[$insurance] ?? $insurance;

// Translate reason
$reasonTypes = [
    'erstbesuch' => 'Erstbesuch',
    'kontrolluntersuchung' => 'Kontrolluntersuchung',
    'vorsorge' => 'Vorsorgeuntersuchung',
    'impfung' => 'Impfung',
    'attest' => 'Attest/Bescheinigung',
    'akute-beschwerden' => 'Akute Beschwerden',
    'sonstiges' => 'Sonstiges'
];
$reasonText = $reasonTypes[$reason] ?? $reason;

// Format date
$appointmentDateFormatted = date('d.m.Y', strtotime($appointmentDate));
$timeText = $appointmentTime ? $appointmentTime . ' Uhr' : 'Keine spezifische Zeit angegeben';

// Email body (HTML)
$emailBody = '
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2c5f7c; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f7fafc; padding: 30px; }
        .info-row { margin: 15px 0; }
        .label { font-weight: bold; color: #2c5f7c; }
        .value { margin-left: 10px; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Neue Terminanfrage</h2>
        </div>
        <div class="content">
            <h3>Patienteninformationen</h3>
            <div class="info-row">
                <span class="label">Name:</span>
                <span class="value">' . $firstName . ' ' . $lastName . '</span>
            </div>
            <div class="info-row">
                <span class="label">Geburtsdatum:</span>
                <span class="value">' . date('d.m.Y', strtotime($birthdate)) . '</span>
            </div>
            <div class="info-row">
                <span class="label">Versicherung:</span>
                <span class="value">' . $insuranceText . '</span>
            </div>

            <h3 style="margin-top: 30px;">Kontaktdaten</h3>
            <div class="info-row">
                <span class="label">E-Mail:</span>
                <span class="value">' . $email . '</span>
            </div>
            <div class="info-row">
                <span class="label">Telefon:</span>
                <span class="value">' . $phone . '</span>
            </div>

            <h3 style="margin-top: 30px;">Termindetails</h3>
            <div class="info-row">
                <span class="label">Wunschtermin:</span>
                <span class="value">' . $appointmentDateFormatted . '</span>
            </div>
            <div class="info-row">
                <span class="label">Wunschzeit:</span>
                <span class="value">' . $timeText . '</span>
            </div>
            <div class="info-row">
                <span class="label">Grund des Besuchs:</span>
                <span class="value">' . $reasonText . '</span>
            </div>';

if (!empty($message)) {
    $emailBody .= '
            <h3 style="margin-top: 30px;">Zusätzliche Informationen</h3>
            <div style="background: white; padding: 15px; border-left: 3px solid #2c5f7c; margin-top: 10px;">
                ' . nl2br($message) . '
            </div>';
}

$emailBody .= '
        </div>
        <div class="footer">
            <p>Diese E-Mail wurde automatisch über das Online-Terminformular erstellt.</p>
            <p>Eingegangen am: ' . date('d.m.Y H:i') . ' Uhr</p>
        </div>
    </div>
</body>
</html>
';

// Plain text version for email clients that don't support HTML
$emailBodyPlain = "Neue Terminanfrage\n\n";
$emailBodyPlain .= "PATIENTENINFORMATIONEN\n";
$emailBodyPlain .= "Name: $firstName $lastName\n";
$emailBodyPlain .= "Geburtsdatum: " . date('d.m.Y', strtotime($birthdate)) . "\n";
$emailBodyPlain .= "Versicherung: $insuranceText\n\n";
$emailBodyPlain .= "KONTAKTDATEN\n";
$emailBodyPlain .= "E-Mail: $email\n";
$emailBodyPlain .= "Telefon: $phone\n\n";
$emailBodyPlain .= "TERMINDETAILS\n";
$emailBodyPlain .= "Wunschtermin: $appointmentDateFormatted\n";
$emailBodyPlain .= "Wunschzeit: $timeText\n";
$emailBodyPlain .= "Grund: $reasonText\n";
if (!empty($message)) {
    $emailBodyPlain .= "\nZUSÄTZLICHE INFORMATIONEN\n$message\n";
}
$emailBodyPlain .= "\n---\nEingegangen am: " . date('d.m.Y H:i') . " Uhr";

// ==========================================
// Generate iCalendar file
// ==========================================

$calendarService = new CalendarService();
$appointmentData = [
    'firstName' => $firstName,
    'lastName' => $lastName,
    'email' => $email,
    'appointmentDate' => $appointmentDate,
    'appointmentTime' => $appointmentTime,
    'reason' => $reason
];

$icsContent = $calendarService->generateICalendar($appointmentData);
$icsFilename = 'termin-' . date('Ymd') . '-' . uniqid();
$icsFilepath = $calendarService->saveICalendarFile($icsContent, $icsFilename);

// ==========================================
// Send Email with iCalendar attachment
// ==========================================

// Create boundary for multipart email
$boundary = md5(time());

// Email headers with attachment support
$headers = [];
$headers[] = 'MIME-Version: 1.0';
$headers[] = 'From: Terminbuchung <noreply@praxis.de>';
$headers[] = 'Reply-To: ' . $email;
$headers[] = 'X-Mailer: PHP/' . phpversion();
$headers[] = 'Content-Type: multipart/mixed; boundary="' . $boundary . '"';

// Create multipart email body
$multipartBody = "--" . $boundary . "\r\n";
$multipartBody .= "Content-Type: text/html; charset=UTF-8\r\n";
$multipartBody .= "Content-Transfer-Encoding: 7bit\r\n\r\n";
$multipartBody .= $emailBody . "\r\n\r\n";

// Add iCalendar attachment
$multipartBody .= "--" . $boundary . "\r\n";
$multipartBody .= "Content-Type: text/calendar; method=REQUEST; charset=UTF-8; name=\"" . $icsFilename . ".ics\"\r\n";
$multipartBody .= "Content-Transfer-Encoding: base64\r\n";
$multipartBody .= "Content-Disposition: attachment; filename=\"" . $icsFilename . ".ics\"\r\n\r\n";
$multipartBody .= chunk_split(base64_encode($icsContent)) . "\r\n";
$multipartBody .= "--" . $boundary . "--";

try {
    $mailSent = mail($to, $subject, $multipartBody, implode("\r\n", $headers));

    if ($mailSent) {
        // Send confirmation email to patient with calendar attachment
        $confirmSubject = 'Bestätigung Ihrer Terminanfrage';
        $confirmBody = '
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #2c5f7c; color: white; padding: 20px; text-align: center; }
                .content { padding: 30px; background-color: #f7fafc; }
                .calendar-info { background: #e8f4f2; padding: 15px; border-radius: 8px; margin: 20px 0; }
                .calendar-info h4 { color: #2c5f7c; margin-top: 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Terminanfrage erhalten</h2>
                </div>
                <div class="content">
                    <p>Sehr geehrte/r ' . $firstName . ' ' . $lastName . ',</p>
                    <p>vielen Dank für Ihre Terminanfrage über unser Online-Formular.</p>
                    <p><strong>Ihre Angaben:</strong></p>
                    <ul>
                        <li>Wunschtermin: ' . $appointmentDateFormatted . '</li>
                        <li>Wunschzeit: ' . $timeText . '</li>
                        <li>Grund: ' . $reasonText . '</li>
                    </ul>

                    <div class="calendar-info">
                        <h4>📅 Kalender-Integration</h4>
                        <p>Im Anhang finden Sie eine Kalenderdatei (.ics), die Sie in Ihren digitalen Kalender (Outlook, Apple Kalender, Google Kalender, etc.) importieren können.</p>
                        <p><strong>So geht\'s:</strong></p>
                        <ul>
                            <li>Öffnen Sie die angehängte .ics-Datei</li>
                            <li>Ihr Kalender-Programm öffnet sich automatisch</li>
                            <li>Bestätigen Sie das Hinzufügen des Termins</li>
                        </ul>
                        <p style="font-size: 0.9em; color: #666;">Der Termin wird als "vorläufig" markiert, bis wir ihn bestätigt haben.</p>
                    </div>

                    <p>Wir werden Ihre Anfrage schnellstmöglich bearbeiten und uns in Kürze bei Ihnen melden, um den Termin zu bestätigen oder einen alternativen Termin vorzuschlagen.</p>
                    <p>Bei dringenden Anliegen erreichen Sie uns telefonisch unter: <strong>+49 123 456 7890</strong></p>
                    <p>Mit freundlichen Grüßen,<br>Ihr Praxisteam</p>
                </div>
            </div>
        </body>
        </html>
        ';

        // Create multipart email with calendar attachment for patient
        $confirmBoundary = md5(time() . 'confirm');

        $confirmHeaders = [];
        $confirmHeaders[] = 'MIME-Version: 1.0';
        $confirmHeaders[] = 'From: Praxis für Gefäßmedizin <noreply@praxis.de>';
        $confirmHeaders[] = 'X-Mailer: PHP/' . phpversion();
        $confirmHeaders[] = 'Content-Type: multipart/mixed; boundary="' . $confirmBoundary . '"';

        $confirmMultipartBody = "--" . $confirmBoundary . "\r\n";
        $confirmMultipartBody .= "Content-Type: text/html; charset=UTF-8\r\n";
        $confirmMultipartBody .= "Content-Transfer-Encoding: 7bit\r\n\r\n";
        $confirmMultipartBody .= $confirmBody . "\r\n\r\n";

        // Add iCalendar attachment
        $confirmMultipartBody .= "--" . $confirmBoundary . "\r\n";
        $confirmMultipartBody .= "Content-Type: text/calendar; method=REQUEST; charset=UTF-8; name=\"termin.ics\"\r\n";
        $confirmMultipartBody .= "Content-Transfer-Encoding: base64\r\n";
        $confirmMultipartBody .= "Content-Disposition: attachment; filename=\"termin.ics\"\r\n\r\n";
        $confirmMultipartBody .= chunk_split(base64_encode($icsContent)) . "\r\n";
        $confirmMultipartBody .= "--" . $confirmBoundary . "--";

        mail($email, $confirmSubject, $confirmMultipartBody, implode("\r\n", $confirmHeaders));

        // Success response
        echo json_encode([
            'success' => true,
            'message' => 'Vielen Dank! Ihre Terminanfrage wurde erfolgreich gesendet. Wir haben Ihnen eine Bestätigung per E-Mail geschickt und melden uns in Kürze bei Ihnen.'
        ]);
    } else {
        throw new Exception('Mail konnte nicht gesendet werden.');
    }
} catch (Exception $e) {
    // Log error (in production, log to file instead of displaying)
    error_log('Appointment Form Error: ' . $e->getMessage());

    echo json_encode([
        'success' => false,
        'message' => 'Es ist ein Fehler beim Versenden aufgetreten. Bitte versuchen Sie es später erneut oder kontaktieren Sie uns telefonisch unter +49 123 456 7890.'
    ]);
}
?>
