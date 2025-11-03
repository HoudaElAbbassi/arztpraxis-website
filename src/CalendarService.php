<?php
/**
 * CalendarService - iCalendar and CalDAV integration
 * Handles creation of .ics files and calendar events
 */

namespace Arztpraxis;

class CalendarService {

    private $practiceEmail = 'praxis@beispiel.de';
    private $practiceName = 'Praxis für Gefäßmedizin Remscheid';
    private $practiceAddress = 'Musterstraße 123, 12345 Musterstadt';

    /**
     * Generate iCalendar (.ics) content for an appointment
     *
     * @param array $appointmentData Appointment details
     * @return string iCalendar formatted content
     */
    public function generateICalendar($appointmentData) {
        // Extract appointment data
        $firstName = $appointmentData['firstName'] ?? '';
        $lastName = $appointmentData['lastName'] ?? '';
        $email = $appointmentData['email'] ?? '';
        $appointmentDate = $appointmentData['appointmentDate'] ?? '';
        $appointmentTime = $appointmentData['appointmentTime'] ?? '09:00';
        $reason = $appointmentData['reason'] ?? '';

        // Create unique ID for event
        $uid = uniqid('appointment-', true) . '@praxis-gefaessmedizin.de';

        // Parse date and time
        $dateTime = new \DateTime($appointmentDate . ' ' . $appointmentTime);
        $startTime = $dateTime->format('Ymd\THis');

        // Set duration to 30 minutes (default appointment length)
        $dateTime->modify('+30 minutes');
        $endTime = $dateTime->format('Ymd\THis');

        // Current timestamp for DTSTAMP
        $now = new \DateTime();
        $timestamp = $now->format('Ymd\THis\Z');

        // Translate reason to German description
        $reasonDescriptions = [
            'erstbesuch' => 'Erstbesuch',
            'kontrolluntersuchung' => 'Kontrolluntersuchung',
            'vorsorge' => 'Vorsorgeuntersuchung',
            'akute-beschwerden' => 'Akute Beschwerden',
            'sonstiges' => 'Sonstiges'
        ];
        $reasonText = $reasonDescriptions[$reason] ?? $reason;

        // Build iCalendar content
        $icsContent = "BEGIN:VCALENDAR\r\n";
        $icsContent .= "VERSION:2.0\r\n";
        $icsContent .= "PRODID:-//Praxis für Gefäßmedizin//Appointment System//DE\r\n";
        $icsContent .= "CALSCALE:GREGORIAN\r\n";
        $icsContent .= "METHOD:REQUEST\r\n";
        $icsContent .= "X-WR-CALNAME:Arzttermin\r\n";
        $icsContent .= "X-WR-TIMEZONE:Europe/Berlin\r\n";

        // Add timezone information
        $icsContent .= "BEGIN:VTIMEZONE\r\n";
        $icsContent .= "TZID:Europe/Berlin\r\n";
        $icsContent .= "BEGIN:DAYLIGHT\r\n";
        $icsContent .= "TZOFFSETFROM:+0100\r\n";
        $icsContent .= "TZOFFSETTO:+0200\r\n";
        $icsContent .= "DTSTART:19700329T020000\r\n";
        $icsContent .= "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\r\n";
        $icsContent .= "TZNAME:CEST\r\n";
        $icsContent .= "END:DAYLIGHT\r\n";
        $icsContent .= "BEGIN:STANDARD\r\n";
        $icsContent .= "TZOFFSETFROM:+0200\r\n";
        $icsContent .= "TZOFFSETTO:+0100\r\n";
        $icsContent .= "DTSTART:19701025T030000\r\n";
        $icsContent .= "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\r\n";
        $icsContent .= "TZNAME:CET\r\n";
        $icsContent .= "END:STANDARD\r\n";
        $icsContent .= "END:VTIMEZONE\r\n";

        // Add event
        $icsContent .= "BEGIN:VEVENT\r\n";
        $icsContent .= "UID:" . $uid . "\r\n";
        $icsContent .= "DTSTAMP:" . $timestamp . "\r\n";
        $icsContent .= "DTSTART;TZID=Europe/Berlin:" . $startTime . "\r\n";
        $icsContent .= "DTEND;TZID=Europe/Berlin:" . $endTime . "\r\n";
        $icsContent .= "SUMMARY:Arzttermin - " . $reasonText . "\r\n";
        $icsContent .= "DESCRIPTION:Terminanfrage bei " . $this->practiceName . "\\n\\n";
        $icsContent .= "Patient: " . $firstName . " " . $lastName . "\\n";
        $icsContent .= "Grund: " . $reasonText . "\\n\\n";
        $icsContent .= "Bitte beachten Sie\\, dass dieser Termin noch bestätigt werden muss.\\n";
        $icsContent .= "Wir melden uns in Kürze bei Ihnen.\r\n";
        $icsContent .= "LOCATION:" . $this->practiceAddress . "\r\n";
        $icsContent .= "ORGANIZER;CN=" . $this->practiceName . ":mailto:" . $this->practiceEmail . "\r\n";
        $icsContent .= "ATTENDEE;CN=" . $firstName . " " . $lastName . ";RSVP=TRUE:mailto:" . $email . "\r\n";
        $icsContent .= "STATUS:TENTATIVE\r\n";
        $icsContent .= "SEQUENCE:0\r\n";
        $icsContent .= "BEGIN:VALARM\r\n";
        $icsContent .= "TRIGGER:-PT24H\r\n";
        $icsContent .= "ACTION:DISPLAY\r\n";
        $icsContent .= "DESCRIPTION:Erinnerung: Arzttermin morgen\r\n";
        $icsContent .= "END:VALARM\r\n";
        $icsContent .= "END:VEVENT\r\n";
        $icsContent .= "END:VCALENDAR\r\n";

        return $icsContent;
    }

    /**
     * Save iCalendar file to disk
     *
     * @param string $icsContent iCalendar content
     * @param string $filename Filename without extension
     * @return string Full path to saved file
     */
    public function saveICalendarFile($icsContent, $filename) {
        $uploadsDir = __DIR__ . '/../uploads/calendars';

        // Create directory if it doesn't exist
        if (!is_dir($uploadsDir)) {
            mkdir($uploadsDir, 0755, true);
        }

        $filepath = $uploadsDir . '/' . $filename . '.ics';
        file_put_contents($filepath, $icsContent);

        return $filepath;
    }

    /**
     * Generate CalDAV URL for an appointment
     *
     * @param string $uid Unique ID of the appointment
     * @return string CalDAV URL
     */
    public function getCalDAVUrl($uid) {
        // This would point to your CalDAV server
        // For now, returning a placeholder
        $baseUrl = 'https://praxis-gefaessmedizin.de/caldav';
        return $baseUrl . '/appointments/' . $uid . '.ics';
    }

    /**
     * Create email attachment for iCalendar
     *
     * @param string $icsContent iCalendar content
     * @param string $filename Filename
     * @return array Email attachment data
     */
    public function createEmailAttachment($icsContent, $filename) {
        return [
            'content' => chunk_split(base64_encode($icsContent)),
            'filename' => $filename . '.ics',
            'mime_type' => 'text/calendar; method=REQUEST; charset=UTF-8',
            'disposition' => 'attachment'
        ];
    }

    /**
     * Generate webcal:// link for calendar subscription
     *
     * @param string $calendarId Calendar identifier
     * @return string Webcal URL
     */
    public function generateWebcalLink($calendarId) {
        $baseUrl = 'webcal://praxis-gefaessmedizin.de/caldav';
        return $baseUrl . '/calendars/' . $calendarId;
    }
}
