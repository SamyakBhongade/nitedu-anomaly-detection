# 🛡️ Cognitive Cyber Defense - Anomaly Detection for nitedu.in

Real-time network anomaly detection system using LSTM Autoencoder + Isolation Forest hybrid model to secure nitedu.in domain.

## 🎯 Features
- **Real-time Detection**: Sub-second anomaly detection
- **Hybrid ML Model**: LSTM + Isolation Forest fusion
- **Edge Protection**: Cloudflare Worker integration
- **Free Deployment**: Render + Cloudflare (100% free)
- **WebSocket Alerts**: Live security notifications

## 🏗️ Architecture
```
nitedu.in → Cloudflare Worker → Render Backend → ML Detection → Real-time Alerts
```

## 🚀 Quick Deploy

### 1. Deploy to Render
- Connect this GitHub repo to Render
- Uses render.yaml for automatic configuration
- Models train automatically during build

### 2. Deploy Cloudflare Worker
```bash
cd cloudflare
wrangler deploy
```

## 📊 API Endpoints
- `POST /api/v1/ingest` - Event ingestion
- `GET /api/v1/alerts` - Get alerts
- `WS /ws/alerts` - Real-time alerts

## 🔒 Security Protection
- DDoS detection and mitigation
- SQL injection blocking
- Bot/scraper detection
- Geographic anomaly detection
- Real-time threat analysis

## 💰 Cost
**$0/month** - Completely free using Cloudflare + Render free tiers

## 🛠️ Tech Stack
- **Backend**: FastAPI + SQLite
- **ML**: PyTorch LSTM + scikit-learn Isolation Forest
- **Edge**: Cloudflare Workers
- **Deployment**: Render (free hosting)

Protecting **nitedu.in** with enterprise-grade ML security! 🚀