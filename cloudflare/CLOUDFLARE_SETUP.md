# Cloudflare Worker Setup

## Deploy Worker
```bash
wrangler deploy
```

## Configure Routes
1. Go to Cloudflare Dashboard
2. Add route: `nitedu.in/*`
3. Select your worker

## Environment Variables
- Set BACKEND_URL in worker settings