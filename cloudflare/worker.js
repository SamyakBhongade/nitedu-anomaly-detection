export default {
  async fetch(request) {
    return new Response(`
      <h1>🛡️ nitedu.in Protection Active</h1>
      <p>Cognitive Cyber Defense System</p>
      <p>Status: OPERATIONAL</p>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};