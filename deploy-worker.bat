@echo off
echo 🚀 Deploying Cloudflare Worker for nitedu.in protection...
cd cloudflare\nitedu-protection
call npm run deploy
echo ✅ Worker deployed! Check Cloudflare dashboard for status.
pause