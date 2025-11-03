// Netlify Function to send confirmation emails
exports.handler = async (event, context) => {
  // Check for admin password
  const adminPassword = event.headers['x-admin-password'];
  const correctPassword = process.env.ADMIN_PASSWORD || 'admin123';

  if (adminPassword !== correctPassword) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: 'Unauthorized' })
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { email, firstName, lastName, appointmentDate, appointmentTime, status } = JSON.parse(event.body);

    // Here you would integrate with an email service like SendGrid, Mailgun, or SMTP
    // For now, this is a placeholder that would need to be configured

    const emailSubject = status === 'approved'
      ? 'Terminbestätigung - Ihr Termin wurde bestätigt'
      : 'Terminanfrage - Leider konnten wir Ihren Wunschtermin nicht bestätigen';

    const emailBody = status === 'approved'
      ? `Sehr geehrte/r ${firstName} ${lastName},\n\nIhr Terminwunsch für den ${appointmentDate} um ${appointmentTime || 'die gewünschte Zeit'} wurde bestätigt.\n\nWir freuen uns auf Ihren Besuch!\n\nMit freundlichen Grüßen,\nIhr Praxisteam`
      : `Sehr geehrte/r ${firstName} ${lastName},\n\nLeider konnten wir Ihren Terminwunsch für den ${appointmentDate} nicht bestätigen.\n\nBitte kontaktieren Sie uns telefonisch unter +49 123 456 7890 um einen alternativen Termin zu vereinbaren.\n\nMit freundlichen Grüßen,\nIhr Praxisteam`;

    // TODO: Implement actual email sending with your preferred service
    // Example with SendGrid:
    // const sgMail = require('@sendgrid/mail');
    // sgMail.setApiKey(process.env.SENDGRID_API_KEY);
    // await sgMail.send({
    //   to: email,
    //   from: process.env.FROM_EMAIL,
    //   subject: emailSubject,
    //   text: emailBody
    // });

    console.log('Email would be sent to:', email);
    console.log('Subject:', emailSubject);
    console.log('Body:', emailBody);

    return {
      statusCode: 200,
      body: JSON.stringify({
        success: true,
        message: 'E-Mail-Versand vorbereitet (Email-Service muss noch konfiguriert werden)'
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
