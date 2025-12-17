#!/usr/bin/env python3
"""
Start Flask app with ngrok tunnel for QR code testing
This allows QR codes to be accessible from mobile devices
"""

import os
import sys
import subprocess
import time
import requests
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

def get_ngrok_url():
    """Get the current ngrok tunnel URL"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
            # Fallback to http
            for tunnel in tunnels:
                if tunnel.get('proto') == 'http':
                    return tunnel.get('public_url')
    except:
        pass
    return None

def start_ngrok(port=5000):
    """Start ngrok tunnel"""
    print("🚀 Starting ngrok tunnel...")
    print(f"   Forwarding to localhost:{port}")
    
    # Check if ngrok is installed
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        print(f"   Found ngrok: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ ERROR: ngrok is not installed!")
        print("   Install it from: https://ngrok.com/download")
        print("   Or use: pip install pyngrok")
        return None
    
    # Start ngrok
    try:
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        ngrok_url = get_ngrok_url()
        
        if ngrok_url:
            print(f"✅ ngrok tunnel active!")
            print(f"   Public URL: {ngrok_url}")
            print(f"   Dashboard: http://localhost:4040")
            print(f"\n📝 IMPORTANT: Set this in your .env file:")
            print(f"   BASE_URL={ngrok_url}")
            print(f"\n   Or export it before starting:")
            print(f"   export BASE_URL={ngrok_url}")
            return ngrok_url, ngrok_process
        else:
            print("⚠️  ngrok started but couldn't get URL. Check http://localhost:4040")
            return None, ngrok_process
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def update_env_file(ngrok_url):
    """Update .env file with ngrok URL"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    # Read existing .env
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Update BASE_URL
    env_vars['BASE_URL'] = ngrok_url
    
    # Write back
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Updated .env file with BASE_URL={ngrok_url}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("PhishVision - QR Code Testing with ngrok")
    print("=" * 60)
    print()
    
    ngrok_url, ngrok_process = start_ngrok(port)
    
    if ngrok_url:
        # Update .env file
        update_env_file(ngrok_url)
        
        # Set environment variable for current session
        os.environ['BASE_URL'] = ngrok_url
        
        print("\n" + "=" * 60)
        print("Starting Flask app...")
        print("=" * 60)
        print()
        
        # Start Flask app
        from app import app
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        print("\n❌ Failed to start ngrok. Exiting.")
        sys.exit(1)

