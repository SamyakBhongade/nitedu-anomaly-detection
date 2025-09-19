// Cloudflare Worker for nitedu.in anomaly detection
export default {
  async fetch(request, env, ctx) {
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

    // Send to anomaly detection API (async, non-blocking)
    ctx.waitUntil(sendToAnomalyAPI(eventData, env.ANOMALY_API_URL));

    // Check for immediate threats
    if (await isImmediateThreat(request)) {
      return new Response('Access Denied', { status: 403 });
    }

    // Forward to your actual website
    return fetch(request);
  }
};

async function sendToAnomalyAPI(eventData, apiUrl) {
  try {
    await fetch(`${apiUrl}/api/v1/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventData)
    });
  } catch (error) {
    console.error('Failed to send to anomaly API:', error);
  }
}

async function isImmediateThreat(request) {
  const userAgent = request.headers.get('User-Agent') || '';
  
  // Basic threat detection
  const suspiciousPatterns = [
    /sqlmap/i, /nikto/i, /nmap/i, /masscan/i,
    /\.\.\//, /union.*select/i, /<script/i
  ];
  
  const url = new URL(request.url);
  const fullRequest = `${request.method} ${url.pathname} ${userAgent}`;
  
  return suspiciousPatterns.some(pattern => pattern.test(fullRequest));
}