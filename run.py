#!/usr/bin/env python3
"""
🚀 Anomaly Detection System - One-Click Launcher
Starts all components: Backend, Database API, and Dashboard
"""

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path
<<<<<<< HEAD
import threading

def run_service_in_background(command, cwd=None):
    """Run service in background without opening new window"""
    if cwd is None:
        cwd = os.getcwd()
    
    return subprocess.Popen(
        command,
        shell=True,
        cwd=cwd
    )
=======

def run_command_in_new_window(command, title, cwd=None):
    """Run command in new CMD window"""
    if cwd is None:
        cwd = os.getcwd()
    
    cmd = f'start "{title}" cmd /k "cd /d {cwd} && {command}"'
    subprocess.Popen(cmd, shell=True)
>>>>>>> 75ee2c844d0ab2aa71dede22fdabe2e4a9b05e9c

def main():
    print("🛡️ Anomaly Detection System - Starting All Services")
    print("=" * 60)
    
    # Get project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    dashboard_dir = project_root / "dashboard"
    
    # Check if directories exist
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return
    
    if not dashboard_dir.exists():
        print("❌ Dashboard directory not found!")
        return
    
<<<<<<< HEAD
    print("🚀 Starting services in background...")
    
    processes = []
    
    # 1. Start Backend (ML Detection Engine)
    print("1️⃣ Starting ML Backend on port 8080...")
    backend_cmd = "python -m uvicorn app.main_ml:app --host 127.0.0.1 --port 8080"
    backend_process = run_service_in_background(backend_cmd, str(backend_dir))
    processes.append(backend_process)
=======
    print("🚀 Starting services...")
    
    # 1. Start Backend (ML Detection Engine)
    print("1️⃣ Starting ML Backend on port 8080...")
    backend_cmd = "python -m uvicorn app.main_ml:app --reload --host 127.0.0.1 --port 8080"
    run_command_in_new_window(backend_cmd, "🤖 ML Backend (Port 8080)", str(backend_dir))
>>>>>>> 75ee2c844d0ab2aa71dede22fdabe2e4a9b05e9c
    time.sleep(2)
    
    # 2. Start Database API
    print("2️⃣ Starting Database API on port 5000...")
    db_api_cmd = "python database_api.py"
<<<<<<< HEAD
    db_process = run_service_in_background(db_api_cmd, str(dashboard_dir))
    processes.append(db_process)
    time.sleep(2)
    
    # 3. Start Dashboard Server
    print("3️⃣ Starting Dashboard Server on port 3000...")
    dashboard_cmd = "python dashboard_server.py"
    dashboard_process = run_service_in_background(dashboard_cmd, str(dashboard_dir))
    processes.append(dashboard_process)
    time.sleep(5)
    
    # 4. Check if services are running
    print("4️⃣ Checking services...")
    import requests
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        print("✅ Dashboard server is running")
        webbrowser.open("http://localhost:3000")
    except:
        print("❌ Dashboard server not responding")
        print("   Try running manually: cd dashboard && python dashboard_server.py")
    time.sleep(1)

    # Keep main script running
    try:
        print("\n⏳ Press Ctrl+C to stop all services...")
        print("\n🌐 Services Running:")
        print("   🤖 ML Backend: http://localhost:8080")
        print("   🗄️ Database API: http://localhost:5000")
        print("   📊 Dashboard: http://localhost:3000")
=======
    run_command_in_new_window(db_api_cmd, "🗄️ Database API (Port 5000)", str(dashboard_dir))
    time.sleep(2)
    
    # 3. Open Dashboard in browser
    print("3️⃣ Opening Dashboard in browser...")
    dashboard_path = dashboard_dir / "live_dashboard_fixed.html"
    webbrowser.open(f"file:///{dashboard_path.absolute()}")
    time.sleep(1)
    
    # 4. Open Attack Tester
    print("4️⃣ Opening Attack Tester...")
    attack_tester_path = project_root / "attack_tester.html"
    if attack_tester_path.exists():
        webbrowser.open(f"file:///{attack_tester_path.absolute()}")
    
    print("\n✅ All services started successfully!")
    print("=" * 60)
    print("🌐 Services Running:")
    print("   • ML Backend:     http://localhost:8080")
    print("   • Database API:   http://localhost:5000") 
    print("   • Dashboard:      Opened in browser")
    print("   • Attack Tester:  Opened in browser")
    print("\n🔧 Manual Commands:")
    print("   • Test API:       curl http://localhost:8080/health")
    print("   • View Stats:     curl http://localhost:8080/api/v1/status")
    print("   • Test Attack:    Use Attack Tester in browser")
    print("\n⚠️  Keep all CMD windows open to maintain services")
    print("   Close this window when done testing")
    
    # Keep main script running
    try:
        print("\n⏳ Press Ctrl+C to stop all services...")
>>>>>>> 75ee2c844d0ab2aa71dede22fdabe2e4a9b05e9c
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
<<<<<<< HEAD
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        print("   All services stopped.")
=======
        print("   Close all CMD windows manually")
>>>>>>> 75ee2c844d0ab2aa71dede22fdabe2e4a9b05e9c

if __name__ == "__main__":
    main()