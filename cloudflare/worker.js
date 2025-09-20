export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Log request for anomaly detection
    const eventData = {
      timestamp: Date.now(),
      ip: request.headers.get('CF-Connecting-IP'),
      country: request.cf?.country,
      method: request.method,
      path: url.pathname,
      userAgent: request.headers.get('User-Agent'),
      referer: request.headers.get('Referer')
    };

    // Send to backend for ML analysis
    await fetch('https://your-render-app.onrender.com/api/v1/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventData)
    });

    // Continue to origin
    return fetch(request);
  }
};