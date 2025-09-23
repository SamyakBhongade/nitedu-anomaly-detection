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
    
    // Enhanced attack detection
    let isAttack = false;
    let attackType = 'Normal';
    const path = url.pathname.toLowerCase();
    const query = url.search.toLowerCase();
    const userAgent = trafficData.user_agent.toLowerCase();
    const fullUrl = decodeURIComponent(url.toString().toLowerCase());
    
    // SQL Injection patterns
    const sqlPatterns = ['union', 'select', "' or '", '" or "', "'=''", 'drop table', 'insert into', 'delete from', "'1'='1", '/*', '--', ';--'];
    if (sqlPatterns.some(pattern => fullUrl.includes(pattern) || path.includes(pattern) || query.includes(pattern))) {
      isAttack = true;
      attackType = 'SQL Injection';
    }
    
    // XSS patterns
    const xssPatterns = ['<script', 'alert(', 'onerror=', 'onload=', 'javascript:', '<img src=x'];
    if (xssPatterns.some(pattern => fullUrl.includes(pattern) || path.includes(pattern) || query.includes(pattern))) {
      isAttack = true;
      attackType = 'XSS Attack';
    }
    
    // Bot/Scanner detection
    const botPatterns = ['sqlmap', 'nikto', 'nmap', 'burp', 'zap', 'python-requests', 'curl/'];
    if (botPatterns.some(pattern => userAgent.includes(pattern))) {
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
