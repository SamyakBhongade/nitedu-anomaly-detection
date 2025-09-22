const BACKEND_URL = 'https://nitedu-anomaly-detection.onrender.com';

export default {
  async fetch(request) {
    const startTime = Date.now();
    const url = new URL(request.url);
    const cf = request.cf || {};
    
    // Extract traffic features
    const trafficData = {
      timestamp: new Date().toISOString(),
      method: request.method,
      path: url.pathname,
      query: url.search,
      user_agent: request.headers.get('User-Agent') || '',
      ip: request.headers.get('CF-Connecting-IP') || '',
      country: cf.country || 'Unknown',
      referer: request.headers.get('Referer') || '',
      content_length: parseInt(request.headers.get('Content-Length') || '0'),
      request_size: url.toString().length
    };
    
    // Basic attack detection
    let isAttack = false;
    let attackType = 'Normal';
    const path = url.pathname.toLowerCase();
    const query = url.search.toLowerCase();
    const userAgent = trafficData.user_agent.toLowerCase();
    
    if (path.includes('union') || path.includes('select') || query.includes('union') || query.includes('select')) {
      isAttack = true;
      attackType = 'SQL Injection';
    } else if (path.includes('<script') || query.includes('<script') || query.includes('alert(')) {
      isAttack = true;
      attackType = 'XSS Attack';
    } else if (userAgent.includes('sqlmap') || userAgent.includes('nikto') || userAgent.includes('nmap')) {
      isAttack = true;
      attackType = 'Bot Attack';
    }
    
    trafficData.attack_type = attackType;
    trafficData.is_attack = isAttack;
    trafficData.response_time = Date.now() - startTime;
    
    // Send to ML backend (fire and forget)
    fetch(`${BACKEND_URL}/api/v1/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trafficData)
    }).catch(() => {}); // Ignore errors to not block traffic
    
    if (isAttack) {
      return new Response(`🚨 ${attackType} Blocked by nitedu.in`, { status: 403 });
    }
    
    return new Response('🛡️ nitedu.in Protected - Status: SAFE', { 
      headers: { 'Content-Type': 'text/plain' } 
    });
  }
};
