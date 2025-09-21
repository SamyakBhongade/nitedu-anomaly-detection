#!/usr/bin/env python3
"""
Keep Render backend alive by pinging it regularly
"""
import requests
import time
import threading

def ping_backend():
    """Ping backend every 10 minutes to keep it alive"""
    url = "https://nitedu-anomaly-detection.onrender.com/health"
    
    while True:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(f"[OK] Backend alive: {response.json()}")
            else:
                print(f"[WARN] Backend status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Ping failed: {e}")
        
        # Wait 10 minutes
        time.sleep(600)

def start_keep_alive():
    """Start keep-alive in background thread"""
    thread = threading.Thread(target=ping_backend, daemon=True)
    thread.start()
    print("[INFO] Keep-alive started for nitedu.in backend")

if __name__ == "__main__":
    print("Starting nitedu.in Backend Keep-Alive")
    ping_backend()