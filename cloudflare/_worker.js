export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Extract request data for anomaly detection
    const eventData = {
      src_ip: request.headers.get('CF-Connecting-IP'),
      dst_ip: 'nitedu.in',
      src_port: url.protocol === 'https:' ? 443 : 80,
      dst_port: 80,
      protocol: 'http',
      packet_count: 1,
      byte_count: parseInt(request.headers.get('content-length') || '0'),
      duration: 0.1,
      timestamp: new Date().toISOString(),
      raw_data: {
        method: request.method,
        path: url.pathname,
        user_agent: request.headers.get('User-Agent'),
        country: request.cf?.country,
        asn: request.cf?.asn
      }
    };

    // Send to anomaly detection API (non-blocking)
    try {
      fetch(`${env.ANOMALY_API_URL}/api/v1/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData)
      }).catch(() => {}); // Silent fail
    } catch (error) {
      console.error('Failed to send to anomaly API:', error);
    }

    // Basic threat detection
    const userAgent = request.headers.get('User-Agent') || '';
    const suspiciousPatterns = [
      /sqlmap/i, /nikto/i, /nmap/i, /masscan/i,
      /\.\.\//, /union.*select/i, /<script/i
    ];
    
    const fullRequest = `${request.method} ${url.pathname} ${userAgent}`;
    const isThreat = suspiciousPatterns.some(pattern => pattern.test(fullRequest));
    
    if (isThreat) {
      return new Response('Access Denied - Security Threat Detected', { status: 403 });
    }

    // Return simple response for now (replace with your actual website)
    return new Response(`
      <html>
        <head><title>nitedu.in - Protected by ML Security</title></head>
        <body>
          <h1>Welcome to nitedu.in</h1>
          <p>This site is protected by ML-powered anomaly detection.</p>
          <p>Your request has been analyzed and approved.</p>
          <hr>
          <small>Powered by Cognitive Cyber Defense System</small>
        </body>
      </html>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};