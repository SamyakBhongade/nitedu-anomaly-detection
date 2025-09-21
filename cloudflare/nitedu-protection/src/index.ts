/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Bind resources to your worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname.toLowerCase();
    const userAgent = request.headers.get('User-Agent') || '';
    
    // Attack detection
    let isAttack = false;
    let attackType = 'Normal';
    
    // SQL Injection
    if (path.includes('union') || path.includes('select') || path.includes("' or '")) {
      isAttack = true;
      attackType = 'SQL Injection';
    }
    
    // XSS
    if (path.includes('<script') || path.includes('alert(')) {
      isAttack = true;
      attackType = 'XSS Attack';
    }
    
    // Bot
    if (userAgent.includes('sqlmap') || userAgent.includes('bot')) {
      isAttack = true;
      attackType = 'Bot Attack';
    }
    
    if (isAttack) {
      return new Response(`
        <h1>🚨 Security Alert</h1>
        <p>Attack: ${attackType}</p>
        <p>Blocked by nitedu.in Protection</p>
      `, { status: 403, headers: { 'Content-Type': 'text/html' } });
    }
    
    return new Response(`
      <h1>🛡️ nitedu.in Protected</h1>
      <p>✅ Cognitive Cyber Defense Active</p>
      <p>Status: SAFE</p>
    `, { headers: { 'Content-Type': 'text/html' } });
  }
};
