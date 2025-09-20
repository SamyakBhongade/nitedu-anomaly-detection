export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // Simple anomaly detection
    const path = url.pathname.toLowerCase();
    const userAgent = request.headers.get('User-Agent') || '';
    
    let isAttack = false;
    let attackType = 'Normal';
    
    // Check for SQL injection
    if (path.includes('union') || path.includes('select') || path.includes("' or '")) {
      isAttack = true;
      attackType = 'SQL Injection';
    }
    
    // Check for XSS
    if (path.includes('<script') || path.includes('alert(') || path.includes('javascript:')) {
      isAttack = true;
      attackType = 'XSS Attack';
    }
    
    // Check for bots
    if (userAgent.includes('sqlmap') || userAgent.includes('bot') || userAgent.includes('curl')) {
      isAttack = true;
      attackType = 'Bot Attack';
    }
    
    // Block attacks
    if (isAttack) {
      return new Response(`
        <h1>🚨 Security Alert</h1>
        <p>Attack Type: ${attackType}</p>
        <p>Request blocked by Cognitive Cyber Defense</p>
      `, {
        status: 403,
        headers: { 'Content-Type': 'text/html' }
      });
    }
    
    // Show protection status for normal requests
    return new Response(`
      <h1>🛡️ nitedu.in Protection Active</h1>
      <p>✅ Cognitive Cyber Defense System</p>
      <p>✅ Real-time anomaly detection: ACTIVE</p>
      <p>✅ Attack protection: ENABLED</p>
      <p>Path: ${url.pathname}</p>
      <p>Status: SAFE</p>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};