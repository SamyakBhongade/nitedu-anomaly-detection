const BACKEND_URL = 'https://nitedu-anomaly-detection-7zjn.onrender.com';
const rateLimitMap = new Map();

export default {
  async fetch(request) {
    const startTime = Date.now();
    const url = new URL(request.url);
    const cf = request.cf || {};
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
    
    // Rate Limiting
    const rateLimit = checkRateLimit(clientIP);
    if (rateLimit.blocked) {
      return new Response('Rate limit exceeded', { status: 429, headers: { 'Retry-After': '60' } });
    }
    
    const trafficData = {
      timestamp: new Date().toISOString(),
      method: request.method,
      path: url.pathname,
      query: url.search,
      user_agent: request.headers.get('User-Agent') || '',
      ip: clientIP,
      country: cf.country || 'Unknown',
      referer: request.headers.get('Referer') || '',
      content_length: parseInt(request.headers.get('Content-Length') || '0'),
      request_size: url.toString().length
    };
    
    const fullUrl = decodeURIComponent(url.toString().toLowerCase());
    const userAgent = trafficData.user_agent.toLowerCase();
    
    let isAttack = false;
    let attackType = 'Normal';
    
    // SQL Injection
    const sqlPatterns = ['union', 'select', "' or '", '" or "', "'=''", 'drop table', 'insert into', 'delete from', "'1'='1", '/*', '--', ';--'];
    if (sqlPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'SQL Injection';
    }
    
    // XSS
    const xssPatterns = ['<script', 'alert(', 'onerror=', 'onload=', 'javascript:', '<img src=x', 'onclick='];
    if (!isAttack && xssPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'XSS Attack';
    }
    
    // Bot/Scanner
    const botPatterns = ['sqlmap', 'nikto', 'nmap', 'burp', 'zap', 'python-requests', 'curl/', 'wget'];
    if (!isAttack && botPatterns.some(pattern => userAgent.includes(pattern))) {
      isAttack = true;
      attackType = 'Bot Attack';
    }
    
    // SSRF
    const ssrfPatterns = ['169.254.169.254', 'localhost', '127.0.0.1', 'metadata', '0.0.0.0'];
    if (!isAttack && ssrfPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'SSRF Attack';
    }
    
    // RCE
    const rcePatterns = ['wget', 'curl', 'bash', 'sh', '/bin/', 'exec(', 'system(', 'shell_exec'];
    if (!isAttack && rcePatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'RCE Attack';
    }
    
    // Path Traversal
    const traversalPatterns = ['../', '..\\', '%2e%2e', 'etc/passwd', 'windows/system32', '/etc/shadow'];
    if (!isAttack && traversalPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'Path Traversal';
    }
    
    // NoSQL Injection
    const nosqlPatterns = ['[$ne]', '[$gt]', '[$lt]', '[$regex]', '[$where]', '[$exists]'];
    if (!isAttack && nosqlPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'NoSQL Injection';
    }
    
    // Deserialization
    const deserialPatterns = ['o:', 'a:', 'stdclass', 'unserialize', 'pickle'];
    if (!isAttack && deserialPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'Deserialization';
    }
    
    // XML Injection
    const xmlPatterns = ['<!doctype', '<!entity', 'system', 'file://', '<?xml'];
    if (!isAttack && xmlPatterns.some(pattern => fullUrl.includes(pattern))) {
      isAttack = true;
      attackType = 'XML Injection';
    }
    
    trafficData.attack_type = attackType;
    trafficData.is_attack = isAttack;
    trafficData.response_time = Date.now() - startTime;
    
    // ALWAYS call ML backend for ALL requests (not just advanced threats)
    let mlBlocked = false;
    let mlAttackType = attackType;
    let mlDebug = 'No ML call';
    
    try {
      const mlResponse = await fetch(`${BACKEND_URL}/api/v1/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trafficData),
        signal: AbortSignal.timeout(5000) // 5s timeout
      });
      
      mlDebug = `ML Response: ${mlResponse.status}`;
      
      if (mlResponse.ok) {
        const mlResult = await mlResponse.json();
        mlDebug = `ML Result: ${mlResult.is_anomaly}, Conf: ${mlResult.confidence}`;
        
        // Use ML result if it detects an anomaly
        if (mlResult.is_anomaly && mlResult.confidence > 0.3) {
          mlBlocked = true;
          mlAttackType = `ML: ${mlResult.attack_type || 'Anomaly'}`;
          mlDebug += ' - BLOCKED';
        }
      }
    } catch (e) {
      mlDebug = `ML Error: ${e.message}`;
    }
    
    // Send to ML backend for learning (fire and forget)
    fetch(`${BACKEND_URL}/api/v1/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trafficData)
    }).catch(() => {});
    
    // Use ML detection if available, otherwise fall back to rules
    if (mlBlocked) {
      return new Response(`Attack Blocked: ${mlAttackType}`, { status: 403 });
    }
    if (isAttack) {
      return new Response(`Attack Blocked: ${attackType}`, { status: 403 });
    }
    
    return new Response(`nitedu.in Protected - Status: SAFE\nDebug: ${mlDebug}`, { 
      headers: { 'Content-Type': 'text/plain' } 
    });
  }
};

function checkRateLimit(ip) {
  const now = Date.now();
  const windowMs = 60000;
  const maxRequests = 100;
  
  if (!rateLimitMap.has(ip)) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + windowMs });
    return { blocked: false };
  }
  
  const record = rateLimitMap.get(ip);
  
  if (now > record.resetTime) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + windowMs });
    return { blocked: false };
  }
  
  if (record.count >= maxRequests) {
    return { blocked: true };
  }
  
  record.count++;
  return { blocked: false };
}
