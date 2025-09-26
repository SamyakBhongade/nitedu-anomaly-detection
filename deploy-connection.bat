@echo off
echo 🚀 Connecting Render Backend to Cloudflare Worker
echo ================================================

echo.
echo Step 1: Deploy to Render
echo -------------------------
echo 1. Go to https://render.com
echo 2. Connect your GitHub repo
echo 3. Create new Web Service
echo 4. Use these settings:
echo    - Name: nitedu-anomaly-detection-ml
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: cd backend && python -m uvicorn app.main_ml:app --host 0.0.0.0 --port $PORT
echo    - Health Check Path: /health
echo.
echo Your backend will be available at:
echo https://nitedu-anomaly-detection-ml.onrender.com
echo.

echo Step 2: Deploy Cloudflare Worker
echo ---------------------------------
cd cloudflare\nitedu-protection
echo Installing dependencies...
call npm install
echo.
echo Deploying worker...
call npx wrangler deploy
echo.

echo Step 3: Configure Domain
echo -------------------------
echo 1. Go to Cloudflare Dashboard
echo 2. Add nitedu.in domain
echo 3. Set Worker Route: nitedu.in/*
echo 4. Enable "Bypass Cache on Cookie"
echo.

echo ✅ Connection Setup Complete!
echo.
echo Test your protection:
echo - Normal: https://nitedu.in/
echo - Attack: https://nitedu.in/?id=1' OR '1'='1
echo.
pause