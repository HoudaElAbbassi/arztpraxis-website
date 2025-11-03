// Netlify Function to get form submissions
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
  // Check for admin password in headers
  const adminPassword = event.headers['x-admin-password'];
  const correctPassword = process.env.ADMIN_PASSWORD || 'admin123'; // Change in Netlify env vars

  if (adminPassword !== correctPassword) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: 'Unauthorized' })
    };
  }

  try {
    // Get Netlify API token from environment
    const netlifyToken = process.env.NETLIFY_API_TOKEN;
    const siteId = process.env.SITE_ID;

    if (!netlifyToken || !siteId) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Missing Netlify configuration' })
      };
    }

    // Fetch form submissions from Netlify API
    const response = await fetch(
      `https://api.netlify.com/api/v1/sites/${siteId}/submissions`,
      {
        headers: {
          'Authorization': `Bearer ${netlifyToken}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch submissions');
    }

    const submissions = await response.json();

    // Filter for our form
    const terminanfragen = submissions.filter(sub =>
      sub.form_name === 'terminanfrage'
    );

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(terminanfragen)
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
