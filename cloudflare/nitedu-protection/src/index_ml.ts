/**
 * ML-Powered Cloudflare Worker for nitedu.in Protection
 * Integrates with advanced ML backend for real-time threat detection
 */

interface MLPredictionResponse {
  is_anomaly: boolean;
  confidence: number;
  attack_type: string;
  risk_score?: number;
  method: string;
}

export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
    const userAgent = request.headers.get('User-Agent') || '';
    const country = request.headers.get('CF-IPCountry') || '';
    
    // Prepare event data for ML analysis (decode URLs to catch encoded attacks)
    const decodedPath = decodeURIComponent(url.pathname);
    const decodedQuery = decodeURIComponent(url.search);
    
    const eventData = {
      method: request.method,
      path: decodedPath,
      query: decodedQuery,
      user_agent: userAgent,
      client_ip: clientIP,
      country: country,
      timestamp: new Date().toISOString(),
      headers: Object.fromEntries(request.headers.entries())
    };
    
    try {
      // Call ML backend for prediction
      const mlResponse = await fetch('https://nitedu-anomaly-detection-6w4v.onrender.com/api/v1/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData),
        // Timeout after 5 seconds
        signal: AbortSignal.timeout(5000)
      });
      
      if (mlResponse.ok) {
        const prediction: MLPredictionResponse = await mlResponse.json();
        
        // Debug: Log prediction for testing
        console.log('ML Prediction:', JSON.stringify(prediction));
        
        // Block if ML detects anomaly with medium confidence
        if (prediction.is_anomaly && prediction.confidence > 0.4) {
          return new Response(`
            <html>
              <head><title>🚨 Security Alert - nitedu.in</title></head>
              <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>🛡️ Access Blocked</h1>
                <h2>🚨 ${prediction.attack_type} Detected</h2>
                <p><strong>Confidence:</strong> ${(prediction.confidence * 100).toFixed(1)}%</p>
                <p><strong>Method:</strong> ${prediction.method}</p>
                <p><strong>IP:</strong> ${clientIP}</p>
                <hr>
                <p><em>Protected by Cognitive Cyber Defense</em></p>
                <p><small>nitedu.in Security System</small></p>
              </body>
            </html>
          `, { 
            status: 403, 
            headers: { 
              'Content-Type': 'text/html',
              'X-Blocked-Reason': prediction.attack_type,
              'X-Confidence': prediction.confidence.toString()
            } 
          });
        }
        
        // Allow legitimate traffic but show debug info
        return new Response(`
          <html>
            <head><title>✅ nitedu.in - Access Granted</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
              <h1>🛡️ nitedu.in Protected</h1>
              <h2>✅ Access Granted</h2>
              <p><strong>Status:</strong> Safe Traffic</p>
              <p><strong>Anomaly:</strong> ${prediction.is_anomaly}</p>
              <p><strong>Confidence:</strong> ${(prediction.confidence * 100).toFixed(1)}%</p>
              <p><strong>Attack Type:</strong> ${prediction.attack_type}</p>
              <p><strong>Detection:</strong> ${prediction.method}</p>
              <hr>
              <p><em>Secured by Advanced ML Detection</em></p>
              <p><small>Debug: Threshold=50%, Current=${(prediction.confidence * 100).toFixed(1)}%</small></p>
            </body>
          </html>
        `, { 
          headers: { 
            'Content-Type': 'text/html',
            'X-Protection-Status': 'active',
            'X-ML-Confidence': prediction.confidence.toString(),
            'X-ML-Anomaly': prediction.is_anomaly.toString()
          } 
        });
        
      } else {
        throw new Error(`ML API error: ${mlResponse.status}`);
      }
      
    } catch (error) {
      console.error('ML prediction failed:', error);
      
      // Fallback to basic rule-based detection
      const fallbackResult = basicThreatDetection(eventData);
      
      if (fallbackResult.isAttack) {
        return new Response(`
          <html>
            <head><title>🚨 Security Alert - nitedu.in</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
              <h1>🛡️ Access Blocked</h1>
              <h2>🚨 ${fallbackResult.attackType} Detected</h2>
              <p><strong>Method:</strong> Fallback Rules</p>
              <p><strong>IP:</strong> ${clientIP}</p>
              <hr>
              <p><em>Protected by nitedu.in Security</em></p>
              <p><small>ML backend unavailable - using backup protection</small></p>
            </body>
          </html>
        `, { 
          status: 403, 
          headers: { 
            'Content-Type': 'text/html',
            'X-Blocked-Reason': fallbackResult.attackType,
            'X-Method': 'fallback'
          } 
        });
      }
      
      // Allow traffic if no threats detected
      return new Response(`
        <html>
          <head><title>✅ nitedu.in - Protected</title></head>
          <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🛡️ nitedu.in Protected</h1>
            <h2>✅ Access Granted</h2>
            <p><strong>Status:</strong> Safe Traffic</p>
            <p><strong>Protection:</strong> Active (Fallback Mode)</p>
            <hr>
            <p><em>Secured by nitedu.in Defense System</em></p>
          </body>
        </html>
      `, { 
        headers: { 
          'Content-Type': 'text/html',
          'X-Protection-Status': 'fallback'
        } 
      });
    }
  }
};

/**
 * Fallback basic threat detection when ML backend is unavailable
 */
function basicThreatDetection(eventData: any): { isAttack: boolean; attackType: string } {
  // Decode URLs to catch encoded attacks
  const path = decodeURIComponent(eventData.path || '').toLowerCase();
  const query = decodeURIComponent(eventData.query || '').toLowerCase();
  const userAgent = eventData.user_agent.toLowerCase();
  
  // SQL Injection
  if (path.includes('union') || path.includes('select') || path.includes("' or '") ||
      query.includes('union') || query.includes('select') || query.includes("' or '")) {
    return { isAttack: true, attackType: 'SQL Injection' };
  }
  
  // XSS
  if (path.includes('<script') || path.includes('alert(') ||
      query.includes('<script') || query.includes('alert(')) {
    return { isAttack: true, attackType: 'XSS Attack' };
  }
  
  // Bot/Scanner
  if (userAgent.includes('sqlmap') || userAgent.includes('nikto') || 
      userAgent.includes('curl') || userAgent.includes('python-requests')) {
    return { isAttack: true, attackType: 'Bot Attack' };
  }
  
  return { isAttack: false, attackType: 'Normal' };
}